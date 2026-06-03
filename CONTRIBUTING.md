# Contributing to NoteForge-AI

Thanks for helping improve NoteForge-AI. The project is early and practical contributions are especially valuable.

## Good First Contributions

- Add a new example note and expected output under `examples/`.
- Improve one prompt in `backend/app/prompts/`.
- Add provider setup notes for OpenAI-compatible services.
- Improve error messages for common setup failures.
- Polish mobile layouts in the writing and assessment pages.

## Local Checks

Run the frontend build:

```powershell
cd frontend
npm.cmd run build
```

Run a backend syntax check:

```powershell
python -m compileall backend\app
```

## Development Notes

- Keep the real writing workflow BYOK. Do not commit API keys or generated private content.
- Demo endpoints should use local canned data only.
- Prefer small, reviewable changes.
- When changing prompts, include a short example or before/after note in the pull request.
- When changing UI, make sure the page still works on narrow screens.

## Pull Request Checklist

- The frontend build passes.
- Backend modules compile.
- New user-facing behavior is documented in `README.md` or `README.zh-CN.md`.
- Any new generated runtime files are ignored by Git.
- Secrets and local storage output are not committed.
