# Claude Code

> Learn how to use Claude Code with OpenRouter to access various models.

<Warning>
  Claude Code is a powerful agentic tool. While you can use any model via OpenRouter, we recommend sticking to highly capable models (like Claude Opus 4.5, GPT 5.2, etc.) for the best experience, as complex coding tasks require strong reasoning.
</Warning>

## Quick Start

This guide will get you running [Claude Code](https://code.claude.com/docs/en/overview) powered by OpenRouter in just a few minutes.

### Step 1: Install Claude Code

<Tabs>
  <Tab title="Native Install (Recommended)">
    **macOS, Linux, WSL:**

    ```bash
    curl -fsSL https://claude.ai/install.sh | bash
    ```

    **Windows PowerShell:**

    ```powershell
    irm https://claude.ai/install.ps1 | iex
    ```
  </Tab>

  <Tab title="npm">
    Requires [Node.js 18 or newer](https://nodejs.org/en/download/).

    ```bash
    npm install -g @anthropic-ai/claude-code
    ```
  </Tab>
</Tabs>

### Step 2: Connect Claude to OpenRouter

Instead of logging in with Anthropic directly, connect Claude Code to OpenRouter.
This requires setting a few environment variables.

Requirements:

1. Use `https://openrouter.ai/api` for the base url
2. Provide your OpenRouter API key as the auth token
3. **Important:** Explicitly blank out the Anthropic API key to prevent conflicts

<Tabs>
  <Tab title="Shell Profile">
    Add these environment variables to your shell profile:

    ```bash
    # Set these in your shell (e.g., ~/.bashrc, ~/.zshrc)
    export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
    export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
    export ANTHROPIC_API_KEY="" # Important: Must be explicitly empty
    ```

    <Note>
      **Persistence:** We recommend adding these lines to your shell profile (`~/.bashrc`, `~/.zshrc`, or `~/.config/fish/config.fish`).
    </Note>
  </Tab>

  <Tab title="Project Settings File">
    Alternatively, you can configure Claude Code using a project-level settings file at `.claude/settings.local.json` in your project root:

    ```json
    {
      "env": {
        "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
        "ANTHROPIC_AUTH_TOKEN": "<your-openrouter-api-key>",
        "ANTHROPIC_API_KEY": ""
      }
    }
    ```

    Replace `<your-openrouter-api-key>` with your actual OpenRouter API key.

    <Note>
      **Note:** This method keeps your configuration scoped to the project, making it easy to share OpenRouter settings with your team via version control (just be careful not to commit your API key).
    </Note>
  </Tab>
</Tabs>

<Warning>
  Do not put these in a project-level `.env` file. The native Claude Code installer does not read standard `.env` files.
</Warning>

### Step 3: Start your session

Navigate to your project directory and start Claude Code:

```bash
cd /path/to/your/project
claude
```

You are now connected! Any prompt you send will be routed through OpenRouter.

### Step 4: Verify

You can confirm your connection by running the `/status` command inside Claude Code.

```text
> /status
Auth token: ANTHROPIC_AUTH_TOKEN
Anthropic base URL: https://openrouter.ai/api
```

You can also check the [OpenRouter Activity Dashboard](https://openrouter.ai/activity) to see your requests appearing in real-time.

## Changing Models

By default, Claude Code uses specific Anthropic models aliases (like "Sonnet", "Opus", "Haiku"). OpenRouter automatically maps these to the correct Anthropic models.

### Overriding Default Models

You can configure Claude Code to use **any model** on OpenRouter (including OpenAI, Google, or Llama models) by overriding the default model aliases using environment variables.

<Warning>
  **Tool Use Required:** Claude Code relies on tool use capabilities to perform actions like reading files, running terminal commands, and editing code. When selecting alternative models, make sure they support tool use. See the [full list of models that support tool use](https://openrouter.ai/models?supported_parameters=tools).
</Warning>

For example, to swap the default "Sonnet" alias for GPT-5.1 Codex Max:

```bash
export ANTHROPIC_DEFAULT_SONNET_MODEL="openai/gpt-5.1-codex-max"
```

You can override other tiers as well:

```bash
export ANTHROPIC_DEFAULT_OPUS_MODEL="openai/gpt-5.2-pro"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="minimax/minimax-m2:exacto"
```

<Info>
  **Tip:** While you can use any model, Claude Code relies deeply on agentic behaviors (tool use, precise formatting). For best results, we recommend [using Exacto](/docs/features/exacto)â€”our specialized coding and tool-use modelâ€”designed for strong code generation and reliable agentic performance. Learn more about Exacto on our [Exacto variant page](docs/guides/routing/model-variants/exacto).
</Info>

### Advanced Configuration with Presets

For more complex configurationsâ€”such as defining fallback models, custom system prompts, or specific provider routingâ€”you can use [OpenRouter Presets](/docs/features/presets).

1. Create a preset at [openrouter.ai/settings/presets](https://openrouter.ai/settings/presets) (e.g., with slug `my-coding-setup`).
2. Use the preset as your model override:

```bash
export ANTHROPIC_DEFAULT_SONNET_MODEL="@preset/my-coding-setup"
```

This allows you to manage model settings and fallbacks on OpenRouter without changing your local environment variables.

## How It Works

OpenRouter exposes an input that is compatible with the Anthropic Messages API.

1. **Direct Connection:** When you set `ANTHROPIC_BASE_URL` to `https://openrouter.ai/api`, Claude Code speaks its native protocol directly to OpenRouter. No local proxy server is required.
2. **Anthropic Skin:** OpenRouter's "Anthropic Skin" behaves exactly like the Anthropic API. It handles model mapping and passes through advanced features like "Thinking" blocks and native tool use.
3. **Billing:** You are billed using your OpenRouter credits. Usage (including reasoning tokens) appears in your OpenRouter dashboard.

## Agent SDK

The [Anthropic Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) lets you build AI agents programmatically using Python or TypeScript. Since the Agent SDK uses Claude Code as its runtime, you can connect it to OpenRouter using the same environment variables described above.

For complete setup instructions and code examples, see our [Anthropic Agent SDK integration guide](/docs/guides/community/anthropic-agent-sdk).

## GitHub Action

You can use OpenRouter with the official [Claude Code GitHub Action](https://github.com/anthropics/claude-code-action).To adapt the [example workflow](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) for OpenRouter, make two changes to the action step:

1. Pass your OpenRouter API key via `anthropic_api_key` (store it as a GitHub secret named `OPENROUTER_API_KEY`)
2. Set the `ANTHROPIC_BASE_URL` environment variable to `https://openrouter.ai/api`

```yaml
- name: Run Claude Code
  uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.OPENROUTER_API_KEY }}
  env:
    ANTHROPIC_BASE_URL: https://openrouter.ai/api
```

## Troubleshooting

* **Tool Use Errors:** If you see errors about tool use not being supported, the model you selected does not support tool use capabilities. Claude Code requires tool use to read files, run commands, and edit code. Switch to a [model that supports tool use](https://openrouter.ai/models?supported_parameters=tools).
* **Auth Errors:** Ensure `ANTHROPIC_API_KEY` is set to an empty string (`""`). If it is unset (null), Claude Code might fall back to its default behavior and try to authenticate with Anthropic servers.
* **Context Length Errors:** If you swap deep-reasoning tasks to smaller models, you may hit context limits. Use models with at least 128k context windows for best results.
* **Privacy:** OpenRouter does not log your source code prompts unless you explicitly opt-in to prompt logging in your account settings. See our [Privacy Policy](/privacy) for details.