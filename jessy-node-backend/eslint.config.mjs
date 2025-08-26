import js from "@eslint/js";
import typescriptEslintParser from "@typescript-eslint/parser";
import typescriptEslintPlugin from "@typescript-eslint/eslint-plugin";

export default [
  {
    files: ["**/*.ts", "**/*.ts"],
    languageOptions: {
      parser: typescriptEslintParser,
      parserOptions: {
        project: "./tsconfig.json"
      }
    },
    plugins: {
      "@typescript-eslint": typescriptEslintPlugin
    },
    rules: {
      ...typescriptEslintPlugin.configs.recommended.rules
    },
    ignores: ["node_modules", "dist", ".env"]
  },
  {
    files: ["**/*.js"],
    languageOptions: {
      parser: js
    },
    plugins: {},
    rules: {},
    ignores: ["node_modules", "dist", ".env"]
  },
  {
    files: ["**/*.{js,ts,ts}"],
    rules: {},
    ignores: ["node_modules", "dist", ".env"]
  },
  prettier
];
