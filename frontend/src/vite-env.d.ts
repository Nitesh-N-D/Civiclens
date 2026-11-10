/// <reference types="vite/client" />

interface ImportMetaEnv {
  // Public backend origin for split hosting (e.g. Cloudflare Pages + Render). Not a secret.
  readonly VITE_API_BASE?: string;
}
