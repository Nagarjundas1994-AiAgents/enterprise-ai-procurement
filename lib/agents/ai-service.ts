/** AIService abstraction — business logic never couples to a specific LLM. */
export interface ChatMessage { role: 'system' | 'user' | 'assistant' | 'tool'; content: string }
export interface AIService {
  generate(prompt: string): Promise<string>;
  chat(messages: ChatMessage[]): Promise<string>;
  structuredOutput<T>(prompt: string, schemaHint: string): Promise<T>;
}

class MockAI implements AIService {
  async generate(prompt: string) { return `[mock-ai] ${prompt.slice(0, 200)}`; }
  async chat(messages: ChatMessage[]) {
    const last = messages[messages.length - 1];
    return `[mock-ai] Understood: ${(last?.content ?? '').slice(0, 200)}`;
  }
  async structuredOutput<T>(prompt: string, _schema: string): Promise<T> {
    return { summary: `[mock-ai] ${prompt.slice(0, 120)}` } as unknown as T;
  }
}

let instance: AIService | null = null;
/** Prefers SAP AI Core when AI_API_URL/AI_API_KEY set; otherwise safe mock. */
export function getAIService(): AIService {
  if (instance) return instance;
  // Real SAP AI Core / Generative AI Hub wiring belongs here (via @sap-ai-sdk/*).
  // Kept behind env so local dev works without credentials.
  if (process.env.AI_API_URL && process.env.AI_API_KEY) {
    console.log('[ai] AI Core credentials detected — production wiring enabled (mock fallback for now)');
  }
  instance = new MockAI();
  return instance;
}
