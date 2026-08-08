export default [
  {
    ignores: ["**/node_modules/**", "**/dist/**", "**/build/**", "**/.turbo/**"],
  },
  {
    files: ["**/*.ts", "**/*.tsx"],
    languageOptions: {
      parser: (await import("typescript-eslint")).default.configs.base,
    },
  },
];