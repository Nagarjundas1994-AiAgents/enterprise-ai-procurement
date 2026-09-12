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

/** OpenAI-compatible chat provider (DeepSeek, AI Core, OpenAI). No SDK needed — plain fetch. */
class OpenAIChatProvider implements AIService {
  private endpoint: string;
  constructor(private baseUrl: string, private apiKey: string, private model: string) {
    const clean = (baseUrl || '').replace(/\/+$/, '');
    this.endpoint = clean.endsWith('/chat/completions') ? clean : `${clean}/chat/completions`;
  }
  private async callChat(messages: ChatMessage[]): Promise<string> {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 30000);
    try {
      const res = await fetch(this.endpoint, {
        method: 'POST',
        headers: { Authorization: `Bearer ${this.apiKey}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: this.model, messages, stream: false }),
        signal: ctrl.signal,
      });
      if (!res.ok) {
        const body = await res.text().catch(() => '');
        throw Object.assign(new Error(`AI provider ${res.status}: ${body.slice(0, 300)}`), {
          code: 'AI_PROVIDER_ERROR',
          status: 502,
        });
      }
      const data: any = await res.json();
      const content = data?.choices?.[0]?.message?.content;
      if (typeof content !== 'string' || !content) throw Object.assign(new Error('AI provider returned empty content'), { code: 'AI_PROVIDER_ERROR', status: 502 });
      return content;
    } finally {
      clearTimeout(timer);
    }
  }
  async generate(prompt: string) {
    return this.callChat([{ role: 'user', content: prompt }]);
  }
  async chat(messages: ChatMessage[]) {
    return this.callChat(messages);
  }
  async structuredOutput<T>(prompt: string, schemaHint: string): Promise<T> {
    const out = await this.callChat([
      { role: 'system', content: `Return ONLY valid JSON matching this shape: ${schemaHint}. No markdown, no explanation.` },
      { role: 'user', content: prompt },
    ]);
    const cleaned = out.replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/\s*```$/i, '').trim();
    try {
      return JSON.parse(cleaned) as T;
    } catch {
      return { raw: out } as unknown as T;
    }
  }
}

/** Test helper — clears cached provider so env changes take effect. */
export function resetAIService(): void {
  instance = null;
}

/**
 * Prefers a real LLM when a key is set, otherwise safe mock.
 * Env (all gitignored, never commit):
 *   AI_API_KEY (or DEEPSEEK_API_KEY) — secret, required for real calls
 *   AI_API_URL  — default https://api.deepseek.com
 *   AI_MODEL    — default deepseek-flash (official API; use deepseek-v4-pro for reasoning-heavy tasks)
 */
export function getAIService(): AIService {
  if (instance) return instance;
  const apiKey = process.env.AI_API_KEY || process.env.DEEPSEEK_API_KEY || '';
  if (apiKey) {
    const baseUrl = process.env.AI_API_URL || 'https://api.deepseek.com';
    const model = process.env.AI_MODEL || 'deepseek-flash';
    // Never log the key itself.
    console.log(`[ai] real LLM enabled provider=${process.env.AI_PROVIDER || 'deepseek'} model=${model} url=${baseUrl}`);
    instance = new OpenAIChatProvider(baseUrl, apiKey, model);
    return instance;
  }
  instance = new MockAI();
  return instance;
}
