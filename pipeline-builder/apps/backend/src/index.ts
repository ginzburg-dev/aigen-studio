import Fastify from "fastify";
import cors from "@fastify/cors";
import {
  compileGraph,
  getSerializableNodeDefinitions,
  graphSchema,
  validateGraph
} from "@pipeline-builder/schema";

const app = Fastify({ logger: true });

await app.register(cors, {
  origin: true
});

app.get("/health", async () => ({ status: "ok" }));

app.get("/node-definitions", async () => ({
  nodes: getSerializableNodeDefinitions()
}));

app.post("/validate", async (request, reply) => {
  const validation = validateGraph(request.body);
  if (!validation.valid) {
    return reply.status(400).send(validation);
  }

  return validation;
});

app.post("/compile", async (request, reply) => {
  const validation = validateGraph(request.body);
  if (!validation.valid) {
    return reply.status(400).send(validation);
  }

  const graph = graphSchema.parse(request.body);
  const instructions = compileGraph(graph);

  return {
    validation,
    instructions
  };
});

const port = Number(process.env.PORT ?? 3001);
const host = process.env.HOST ?? "0.0.0.0";

try {
  await app.listen({ port, host });
} catch (error) {
  app.log.error(error);
  process.exit(1);
}
