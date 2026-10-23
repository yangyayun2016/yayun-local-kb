import type { Recipe } from '../types.ts';

/**
 * NVIDIA NIM exposes OpenAI-compatible chat/completions endpoints.
 * The model ids are provider-qualified, for example `openai/gpt-oss-120b`.
 */
export const nvidia: Recipe = {
  id: 'nvidia',
  name: 'NVIDIA NIM',
  tier: 'openai-compat',
  implementation: 'openai-compatible',
  base_url_default: 'https://integrate.api.nvidia.com/v1',
  auth_env: {
    required: ['NVIDIA_API_KEY'],
    setup_url: 'https://build.nvidia.com/',
  },
  touchpoints: {
    chat: {
      models: ['openai/gpt-oss-120b'],
      supports_tools: true,
      supports_subagent_loop: false,
      supports_prompt_cache: false,
      max_context_tokens: 131072,
      cost_per_1m_input_usd: undefined,
      cost_per_1m_output_usd: undefined,
      price_last_verified: '2026-05-17',
    },
    expansion: {
      models: ['openai/gpt-oss-120b'],
      cost_per_1m_tokens_usd: undefined,
      price_last_verified: '2026-05-17',
    },
  },
  setup_hint: 'Create an NVIDIA NIM API key at https://build.nvidia.com/ and set NVIDIA_API_KEY.',
};
