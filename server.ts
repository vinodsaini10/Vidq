import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Initialize Gemini AI client server-side safely
  let ai: GoogleGenAI | null = null;
  if (process.env.GEMINI_API_KEY) {
    try {
      ai = new GoogleGenAI({
        apiKey: process.env.GEMINI_API_KEY,
        httpOptions: {
          headers: {
            'User-Agent': 'aistudio-build',
          }
        }
      });
    } catch (e) {
      console.warn("Failed to initialize Gemini AI client:", e);
    }
  }

  // Health check endpoint
  app.get("/api/health", (_req, res) => {
    res.json({ status: "ok", service: "VidPulse AI Backend", geminiAvailable: !!ai });
  });

  // AI Content Generation endpoint using Gemini
  app.post("/api/ai/generate", async (req, res) => {
    try {
      const { prompt, type, parameters } = req.body;

      if (!prompt) {
        return res.status(400).json({ error: "Prompt is required" });
      }

      if (!ai) {
        // Fallback realistic AI response generator if API key is not provided yet
        return res.json({
          result: getSimulatedAIResponse(type || 'general', prompt, parameters),
          source: 'simulated'
        });
      }

      const systemInstructions: Record<string, string> = {
        title: "You are an expert YouTube title strategist. Output viral, high CTR title options. Include predicted CTR score (85%-98%) and title type (Curiosity, Urgency, How-To, Story, Authority) for each.",
        script: "You are a master YouTube scriptwriter. Write structured video scripts with [Hook 0-15s], [Intro], [Main Points], [Visual Cues], [CTA], and [Outro]. Estimate video duration and word count.",
        seo: "You are a YouTube SEO Specialist. Analyze the provided topic/title and give a detailed SEO Score (0-100), key recommendation points, primary keywords, secondary tags, and description template.",
        description: "Generate a high-converting, YouTube algorithm friendly video description with key topic summary, chapters/timestamps placeholder, call to action, and relevant hashtags.",
        tags: "Generate 20 high-volume, relevant YouTube tags separated by commas, organized by Primary, LSI/Secondary, and Long-tail keywords.",
        thumbnail: "Generate 3 visual image prompts for Midjourney/Flux for YouTube thumbnails. Include composition advice, primary color palette, text overlay suggestions, and emotion focus.",
        competitor: "Analyze YouTube channel competitors in this niche. List content gaps, viral outlier topics, ideal video length, and posting frequency recommendations."
      };

      const instruction = systemInstructions[type] || "You are an expert AI YouTube SaaS growth consultant.";

      const response = await ai.models.generateContent({
        model: "gemini-3.6-flash",
        contents: prompt,
        config: {
          systemInstruction: instruction,
          temperature: 0.7,
        }
      });

      res.json({
        result: response.text || "No response generated.",
        source: 'gemini'
      });
    } catch (error: any) {
      console.error("AI Generation endpoint error:", error);
      res.status(500).json({
        error: "AI generation failed",
        details: error.message || String(error),
        fallback: getSimulatedAIResponse(req.body.type || 'general', req.body.prompt, req.body.parameters)
      });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`VidPulse AI server running on http://0.0.0.0:${PORT}`);
  });
}

function getSimulatedAIResponse(type: string, prompt: string, parameters?: any): string {
  const topic = prompt.length > 40 ? prompt.substring(0, 40) + '...' : prompt;
  
  if (type === 'title') {
    return JSON.stringify([
      { title: `I Tested ${topic} For 30 Days (SHOCKING Results)`, ctrScore: "96%", type: "Story / Challenge", powerWord: "SHOCKING" },
      { title: `Why 99% of Creators Fail at ${topic} (And How to Fix It)`, ctrScore: "94%", type: "Curiosity / Fear", powerWord: "99% Fail" },
      { title: `The Ultimate ${topic} Blueprint for 2026 [Step-by-Step]`, ctrScore: "91%", type: "How-To / Value", powerWord: "Ultimate" },
      { title: `Stop Doing ${topic} Like This! (Do This Instead)`, ctrScore: "89%", type: "Negative Framing", powerWord: "Stop Doing" },
      { title: `How I Scaled ${topic} to $10,000/Mo Without Showing My Face`, ctrScore: "95%", type: "Financial / Proof", powerWord: "$10,000/Mo" }
    ], null, 2);
  }

  if (type === 'seo') {
    return JSON.stringify({
      overallScore: 88,
      breakdown: {
        titleScore: 92,
        descriptionScore: 84,
        tagRelevance: 90,
        keywordDensity: 86
      },
      strengths: [
        "Strong emotional hook in title",
        "Primary keyword appears in the first 60 characters",
        "Includes high search volume LSI keywords"
      ],
      improvements: [
        "Add timestamps in the description to boost SEO indexing",
        "Include 2 additional call-to-action links above the fold",
        "Increase character count of description from 120 words to 300+ words"
      ]
    }, null, 2);
  }

  return `[VidPulse AI Analysis for "${topic}"]\n\nGenerated custom response tailored to your creator goals with high keyword authority and algorithmic alignment.`;
}

startServer();
