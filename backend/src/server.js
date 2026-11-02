import express from "express";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import OpenAI from "openai";
import crypto from "node:crypto";

const app = express();
app.disable("x-powered-by");
app.use(helmet());
app.use(express.json({ limit: "32kb" }));

const port = Number(process.env.PORT || 8080);
const appToken = process.env.SANTRAM_APP_TOKEN || "";
const apiKey = process.env.OPENAI_API_KEY || "";
const model = process.env.OPENAI_MODEL || "gpt-4.1-mini";
const maxInput = Number(process.env.MAX_INPUT_CHARS || 12000);
const limiter = rateLimit({ windowMs: 60_000, limit: 20, standardHeaders: "draft-7", legacyHeaders: false });

const safeEqual = (a, b) => {
  const aa = Buffer.from(a || "");
  const bb = Buffer.from(b || "");
  return aa.length === bb.length && crypto.timingSafeEqual(aa, bb);
};

app.get("/health", (_req, res) => res.json({ ok: true, service: "santram-ai-api", version: "1.0.0" }));

app.use("/v1", limiter, (req, res, next) => {
  const supplied = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
  if (!appToken || !safeEqual(supplied, appToken)) return res.status(401).json({ error: "unauthorized" });
  next();
});

app.post("/v1/chat", async (req, res) => {
  const messages = req.body?.messages;
  if (!Array.isArray(messages) || messages.length < 1 || messages.length > 30) {
    return res.status(400).json({ error: "messages must contain 1 to 30 items" });
  }
  const normalized = [];
  let total = 0;
  for (const item of messages) {
    if (!item || !["user", "assistant"].includes(item.role) || typeof item.content !== "string") {
      return res.status(400).json({ error: "invalid message format" });
    }
    total += item.content.length;
    if (total > maxInput) return res.status(413).json({ error: "input too large" });
    normalized.push({ role: item.role, content: item.content });
  }
  if (!apiKey) return res.status(503).json({ error: "AI provider is not configured on the server" });

  try {
    const client = new OpenAI({ apiKey, timeout: 45_000, maxRetries: 1 });
    const completion = await client.chat.completions.create({
      model,
      messages: [
        { role: "system", content: "You are SANTRAM AI INFINITY, the business and personal assistant for SANTRAM INDUSTRIES. Respond clearly in the user's language. Never claim to have performed a phone call, WhatsApp message, payment, backup, or device action unless a connected and authorized tool confirms it. Ask for confirmation before external or irreversible actions." },
        ...normalized
      ],
      temperature: 0.4
    });
    res.json({ reply: completion.choices?.[0]?.message?.content || "", model: completion.model });
  } catch (error) {
    const status = error?.status === 429 ? 429 : 502;
    res.status(status).json({ error: "AI request failed", requestId: crypto.randomUUID() });
    console.error("AI provider request failed", { status: error?.status, type: error?.type });
  }
});

app.listen(port, "0.0.0.0", () => console.log(`SANTRAM AI API listening on ${port}`));
