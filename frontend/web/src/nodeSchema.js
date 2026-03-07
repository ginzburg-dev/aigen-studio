// web/src/nodeSchema.js
export const NODE_DEFS = {
  Start: { params: {} },
  End:   { params: {} },

  SetVariable: {
    params: { name: "temp_string", value: "Example variable", mode: "replace" },
  },
  CopyVariable: {
    params: { input: "temp_string", output: "temp_string_copy", mode: "replace" },
  },
  PrintVariable: {
    params: { name: "temp_string_copy" },
  },
  ReadFile: {
    params: { file_path: "././ignore--api-key", output: "api-key", mode: "replace" },
  },
  SaveFile: {
    params: { file_path: "././cache/response.txt", input: "chat_responce_variable" },
  },
  GPTChat: {
    params: {
      prompt: [
        { type: "text",  content: "Describe images." },
        { type: "image", content: "././examples/image_samples/rabbit_pixel_art.png", detailed: true },
        { type: "image", content: "././examples/image_samples/*", detailed: true },
      ],
      "api-key": "api-key",
      max_tokens: 500,
      chat_history: "chat_history_variable",
      output: "chat_responce_variable",
      mode: "replace",
    },
  },
};
