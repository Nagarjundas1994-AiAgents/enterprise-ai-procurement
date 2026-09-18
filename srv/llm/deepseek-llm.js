import cds from '@sap/cds';
import { ChatOpenAI } from '@langchain/openai';

const LOG = cds.log('agents');

/**
 * DeepSeek LLM provider for @cap-js/agents (A2A preview + ReAct loop).
 *
 * DeepSeek exposes an OpenAI-compatible API, so ChatOpenAI (with tool
 * calling / bindTools support) is the correct LangChain wrapper — the
 * plain-fetch OpenAIChatProvider in lib/agents/ai-service.ts cannot drive
 * the agent loop because it has no bindTools.
 *
 * Env (gitignored .env, never commit):
 *   AI_API_KEY (or DEEPSEEK_API_KEY) — required for real calls
 *   AI_API_URL  — default https://api.deepseek.com
 *   AI_MODEL    — default deepseek-flash (latest flash tier, verified
 *                 live 2026-09-17 via GET /v1/models)
 *   AI_PROVIDER — informational only (deepseek)
 *
 * cds.requires wiring (package.json):
 *   "llm": { "kind": "deepseek", "model": "deepseek-flash" }
 *   "kinds": { "deepseek": { "impl": "./srv/llm/deepseek-llm.js" } }
 */
export default class DeepSeekChatService extends ChatOpenAI {
  constructor(name, options = {}) {
    const apiKey = options.apiKey || options.credentials?.apiKey || process.env.AI_API_KEY || process.env.DEEPSEEK_API_KEY || '';
    if (!apiKey) {
      throw Object.assign(new Error('DeepSeek LLM misconfigured: set AI_API_KEY (or DEEPSEEK_API_KEY) in .env'), {
        code: 'AI_CONFIG_MISSING',
        status: 500,
      });
    }
    const rawBase = options.baseURL || options.apiUrl || options.credentials?.baseURL || process.env.AI_API_URL || 'https://api.deepseek.com';
    const clean = String(rawBase).replace(/\/+$/, '');
    // OpenAI SDK expects the versioned base (…/v1); accept bare host too.
    const baseURL = /\/v1$/.test(clean) ? clean : `${clean}/v1`;
    const model = options.model || process.env.AI_MODEL || 'deepseek-flash';
    const temperature = options.temperature ?? 0;
    const maxTokens = options.max_tokens ?? options.maxTokens ?? cds.env.agents?.params?.max_tokens ?? 4096;

    super(
      {
        model,
        apiKey,
        configuration: { baseURL },
        temperature,
        maxTokens,
        streaming: options.streaming !== false,
      },
      {},
    );
    this.name = name;
    this.options = { ...options, model, baseURL };
    LOG.info(`Using DeepSeek LLM model=${model} url=${baseURL}`);
  }
}

DeepSeekChatService._is_service_class = true;
