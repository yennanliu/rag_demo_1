/**
 * Unit tests for RAGApp JavaScript class
 * @jest-environment jsdom
 */

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Set localStorage in multiple places to ensure it's available
global.localStorage = localStorageMock;
if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
    writable: true,
    configurable: true
  });
}
// Also make it available as a global variable for the eval'd code
globalThis.localStorage = localStorageMock;

// Mock document elements
document.getElementById = jest.fn((id) => {
  const mockElement = {
    value: '',
    textContent: '',
    innerHTML: '',
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      toggle: jest.fn(),
    },
    style: {},
    scrollTop: 0,
    scrollHeight: 100,
  };
  return mockElement;
});

// Load the RAGApp class
const fs = require('fs');
const path = require('path');
const appJsPath = path.join(__dirname, '../static/app.js');
const appJsContent = fs.readFileSync(appJsPath, 'utf8');

// Extract RAGApp class definition (remove the instantiation at the end)
const classDefinition = appJsContent.substring(
  0,
  appJsContent.indexOf('// Initialize app')
);

// Evaluate the class definition and export it
// Append code to make RAGApp available globally
const codeToEval = classDefinition + '\nif (typeof window !== "undefined") window.RAGApp = RAGApp; if (typeof global !== "undefined") global.RAGApp = RAGApp;';
// eslint-disable-next-line no-eval
eval(codeToEval);
// Get RAGApp from global scope
const RAGApp = global.RAGApp;

describe('RAGApp', () => {
  let app;

  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    fetch.mockClear();

    // Mock console.error to suppress error logs in tests
    jest.spyOn(console, 'error').mockImplementation(() => {});

    // Mock fetch for config
    fetch.mockResolvedValue({
      json: async () => ({
        success: true,
        config: { sample_documents: [] },
      }),
    });

    // Create app instance without calling init
    app = Object.create(RAGApp.prototype);
    app.conversationHistory = [];
    app.sampleDocs = [];
    app.currentConversationId = null;
  });

  describe('Initialization', () => {
    test('should initialize with empty conversation history', () => {
      expect(app.conversationHistory).toEqual([]);
    });

    test('should initialize with empty sample docs', () => {
      expect(app.sampleDocs).toEqual([]);
    });

    test('should initialize with null conversation ID', () => {
      expect(app.currentConversationId).toBeNull();
    });
  });

  describe('LocalStorage Operations', () => {
    test('loadConversationFromLocalStorage should load from localStorage', () => {
      const mockConversation = [
        { role: 'user', content: 'Hello', timestamp: 123 },
        { role: 'assistant', content: 'Hi', timestamp: 124 },
      ];
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockConversation));

      app.loadConversationFromLocalStorage();

      expect(localStorageMock.getItem).toHaveBeenCalledWith('ragConversation');
      expect(app.conversationHistory).toEqual(mockConversation);
    });

    test('loadConversationFromLocalStorage should handle empty localStorage', () => {
      localStorageMock.getItem.mockReturnValue(null);

      app.loadConversationFromLocalStorage();

      expect(app.conversationHistory).toEqual([]);
    });

    test('loadConversationFromLocalStorage should handle invalid JSON', () => {
      localStorageMock.getItem.mockReturnValue('invalid json');

      app.loadConversationFromLocalStorage();

      // Should not throw error, conversation should remain empty
      expect(app.conversationHistory).toEqual([]);
    });

    test('saveConversationToLocalStorage should save to localStorage', () => {
      app.conversationHistory = [
        { role: 'user', content: 'Test', timestamp: 123 },
      ];

      app.saveConversationToLocalStorage();

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'ragConversation',
        JSON.stringify(app.conversationHistory)
      );
    });
  });

  describe('Message Management', () => {
    test('addMessageToChat should add message to conversation', () => {
      app.renderConversation = jest.fn();
      app.saveConversationToLocalStorage = jest.fn();

      app.addMessageToChat('user', 'Hello');

      expect(app.conversationHistory).toHaveLength(1);
      expect(app.conversationHistory[0].role).toBe('user');
      expect(app.conversationHistory[0].content).toBe('Hello');
      expect(app.renderConversation).toHaveBeenCalled();
      expect(app.saveConversationToLocalStorage).toHaveBeenCalled();
    });

    test('addMessageToChat should include sources when provided', () => {
      app.renderConversation = jest.fn();
      app.saveConversationToLocalStorage = jest.fn();

      const sources = ['Source 1', 'Source 2'];
      app.addMessageToChat('assistant', 'Answer', sources);

      expect(app.conversationHistory[0].sources).toEqual(sources);
    });

    test('clearConversation should clear conversation history', () => {
      app.conversationHistory = [{ role: 'user', content: 'Test' }];
      app.renderConversation = jest.fn();
      global.confirm = jest.fn(() => true);

      app.clearConversation();

      expect(app.conversationHistory).toEqual([]);
      expect(app.currentConversationId).toBeNull();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('ragConversation');
    });

    test('clearConversation should not clear if user cancels', () => {
      app.conversationHistory = [{ role: 'user', content: 'Test' }];
      global.confirm = jest.fn(() => false);

      app.clearConversation();

      expect(app.conversationHistory).toHaveLength(1);
    });
  });

  describe('Sample Documents Management', () => {
    test('renderSampleDocs should update badge with count', () => {
      app.sampleDocs = ['Doc 1', 'Doc 2', 'Doc 3'];
      const mockBadge = { textContent: '' };
      const mockContainer = { innerHTML: '' };

      document.getElementById.mockImplementation((id) => {
        if (id === 'sampleCount') return mockBadge;
        if (id === 'sampleDocsList') return mockContainer;
        return { innerHTML: '' };
      });

      app.renderSampleDocs();

      expect(mockBadge.textContent).toBe('3 samples');
    });

    test('addSampleDoc should add new document', () => {
      app.sampleDocs = ['Doc 1'];
      app.renderSampleDocs = jest.fn();

      app.addSampleDoc();

      expect(app.sampleDocs).toHaveLength(2);
      expect(app.sampleDocs[1]).toBe('New sample document');
      expect(app.renderSampleDocs).toHaveBeenCalled();
    });

    test('updateSampleDoc should update document at index', () => {
      app.sampleDocs = ['Doc 1', 'Doc 2'];

      app.updateSampleDoc(0, 'Updated Doc 1');

      expect(app.sampleDocs[0]).toBe('Updated Doc 1');
    });

    test('removeSampleDoc should remove document at index', () => {
      app.sampleDocs = ['Doc 1', 'Doc 2', 'Doc 3'];
      app.renderSampleDocs = jest.fn();

      app.removeSampleDoc(1);

      expect(app.sampleDocs).toEqual(['Doc 1', 'Doc 3']);
      expect(app.renderSampleDocs).toHaveBeenCalled();
    });
  });

  describe('UI Helper Methods', () => {
    test('escapeHtml should escape HTML special characters', () => {
      const input = '<script>alert("XSS")</script>';
      const escaped = app.escapeHtml(input);

      expect(escaped).not.toContain('<script>');
      expect(escaped).toContain('&lt;');
      expect(escaped).toContain('&gt;');
    });

    test('showLoading should toggle loading state', () => {
      const mockElement = {
        classList: { toggle: jest.fn() },
      };
      document.getElementById.mockReturnValue(mockElement);

      app.showLoading('testLoading', true);

      expect(mockElement.classList.toggle).toHaveBeenCalledWith('show', true);
    });

    test('showError should display error message', () => {
      const mockElement = {
        textContent: '',
        classList: { add: jest.fn() },
      };
      document.getElementById.mockReturnValue(mockElement);

      app.showError('testError', 'Test error message');

      expect(mockElement.textContent).toBe('Test error message');
      expect(mockElement.classList.add).toHaveBeenCalledWith('show');
    });

    test('hideMessage should hide message', () => {
      const mockElement = {
        classList: { remove: jest.fn() },
      };
      document.getElementById.mockReturnValue(mockElement);

      app.hideMessage('testMessage');

      expect(mockElement.classList.remove).toHaveBeenCalledWith('show');
    });
  });

  describe('API Integration', () => {
    test('saveConfig should call API with correct data', async () => {
      app.sampleDocs = ['Doc 1', 'Doc 2'];
      app.showLoading = jest.fn();
      app.hideMessage = jest.fn();
      app.showSuccess = jest.fn();

      fetch.mockResolvedValueOnce({
        json: async () => ({ success: true }),
      });

      await app.saveConfig();

      expect(fetch).toHaveBeenCalledWith(
        '/api/config',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });

    test('saveConfig should handle errors', async () => {
      app.showLoading = jest.fn();
      app.hideMessage = jest.fn();
      app.showError = jest.fn();

      fetch.mockResolvedValueOnce({
        json: async () => ({ success: false, error: 'Test error' }),
      });

      await app.saveConfig();

      expect(app.showError).toHaveBeenCalledWith('configError', 'Test error');
    });

    test('exportKnowledgeBase should download JSON file', async () => {
      const mockDocuments = ['Doc 1', 'Doc 2'];
      fetch.mockResolvedValueOnce({
        json: async () => ({
          success: true,
          documents: mockDocuments,
        }),
      });

      // Mock URL and createElement
      global.URL.createObjectURL = jest.fn(() => 'blob:url');
      global.URL.revokeObjectURL = jest.fn();
      const mockAnchor = { click: jest.fn() };
      document.createElement = jest.fn(() => mockAnchor);

      await app.exportKnowledgeBase();

      expect(mockAnchor.click).toHaveBeenCalled();
      expect(global.URL.revokeObjectURL).toHaveBeenCalled();
    });
  });

  describe('Conversation Server Operations', () => {
    test('saveConversationToServer should save to API', async () => {
      app.conversationHistory = [{ role: 'user', content: 'Test' }];
      app.showError = jest.fn();
      global.alert = jest.fn();

      fetch.mockResolvedValueOnce({
        json: async () => ({
          success: true,
          id: 'conv_123',
        }),
      });

      await app.saveConversationToServer();

      expect(fetch).toHaveBeenCalledWith(
        '/api/conversations',
        expect.objectContaining({
          method: 'POST',
        })
      );
      expect(app.currentConversationId).toBe('conv_123');
    });

    test('saveConversationToServer should handle empty conversation', async () => {
      app.conversationHistory = [];
      app.showError = jest.fn();
      app.hideMessage = jest.fn();

      await app.saveConversationToServer();

      expect(app.showError).toHaveBeenCalledWith(
        'queryError',
        'No conversation to save'
      );
    });
  });
});
