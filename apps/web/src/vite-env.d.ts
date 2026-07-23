/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_DEFAULT_LANG: string
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}