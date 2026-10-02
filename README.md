# Paper2WeChat

Paper2WeChat combines source-grounded academic paper analysis and WeChat article formatting in one portable Codex skill.

The repository is being assembled from the existing paper analyzer and formatter. See SKILL.md for the unified workflow and the accepted design at docs/superpowers/specs/2026-10-02-paper2wechat-design.md.

## Configuration

Copy config.example.json to the ignored local file config.json. Analysis and formatting work without WeChat credentials. Set WECHAT_APP_ID and WECHAT_APP_SECRET only when creating drafts. Environment variables take precedence for secrets.
