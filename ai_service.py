"""
LLM Service integration for StudyCraft AI.
Connects to Google Gemini API with exception handling and an interactive simulated demo mode.
"""
from dataclasses import dataclass
from typing import Optional
import time

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


@dataclass
class AIResponse:
    """Standardized response container for all AI operations."""
    success: bool
    content: str
    error: Optional[str] = None
    model_used: str = ""
    is_demo: bool = False
    duration_sec: float = 0.0


class AIService:
    """Wrapper around LLM API with defensive error handling and offline demo capability."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key.strip() if api_key else ""
        self.model_name = model_name
        self._configured = False

        if self.api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self._configured = True
            except Exception:
                self._configured = False

    def is_configured(self) -> bool:
        """Check if a valid API client is initialized."""
        return bool(self.api_key and self._configured and GENAI_AVAILABLE)

    def generate(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.3,
        force_demo: bool = False
    ) -> AIResponse:
        start_time = time.time()

        if force_demo or not self.is_configured():
            if not force_demo and not self.api_key:
                return AIResponse(
                    success=False,
                    content="",
                    error="⚠️ **Gemini API Key Required**: Enter your API key in the sidebar or switch to **'Interactive Demo Mode'**.",
                    model_used="none",
                    is_demo=False,
                    duration_sec=0.0
                )
            return self._generate_simulated_response(prompt, system_instruction, start_time)

        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction if system_instruction else None
            )

            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=2048,
            )

            response = model.generate_content(prompt, generation_config=generation_config)

            if not response.text:
                return AIResponse(
                    success=False,
                    content="",
                    error="The AI model returned an empty response. This might be due to safety filtering.",
                    model_used=self.model_name,
                    is_demo=False,
                    duration_sec=time.time() - start_time
                )

            return AIResponse(
                success=True,
                content=response.text,
                error=None,
                model_used=self.model_name,
                is_demo=False,
                duration_sec=round(time.time() - start_time, 2)
            )

        except Exception as e:
            return AIResponse(
                success=False,
                content="",
                error=self._classify_error(e),
                model_used=self.model_name,
                is_demo=False,
                duration_sec=round(time.time() - start_time, 2)
            )

    def _classify_error(self, exc: Exception) -> str:
        err_str = str(exc).lower()
        if "api_key" in err_str or "permission" in err_str or "403" in err_str:
            return "❌ **Invalid API Key**: Google Gemini rejected the provided API key. Verify it at https://aistudio.google.com/."
        elif "quota" in err_str or "429" in err_str:
            return "⏳ **Rate Limit Exceeded (429)**: Quota limit reached. Please wait 30 seconds or switch to Demo Mode."
        elif "connection" in err_str or "timeout" in err_str:
            return "🌐 **Network Timeout**: Could not connect to Gemini API. Check your internet connection."
        else:
            return f"❌ **API Error**: {exc}"

    def _generate_simulated_response(self, prompt: str, system_instruction: str, start_time: float) -> AIResponse:
        time.sleep(0.6)
        duration = round(time.time() - start_time, 2)
        prompt_lower = prompt.lower()

        if "quiz" in system_instruction.lower() or "causes of world war i" in prompt_lower:
            content = """#### Question 1: What does the 'A' in the M-A-I-N causes of World War I stand for?
A) Armaments
B) Alliances
C) Annexation
D) Aristocracy

**Correct Answer:** B) Alliances
**Explanation:** The M-A-I-N framework stands for Militarism, Alliances, Imperialism, and Nationalism. Secret mutual defense treaties caused a regional dispute to escalate into a world war.
**Concept Tested:** Structural diplomatic causes of World War I.

---

#### Question 2: Which immediate event catalyzed the outbreak of World War I in June 1914?
A) The sinking of the RMS Lusitania
B) The Moroccan Crisis of 1905
C) The assassination of Archduke Franz Ferdinand
D) The signing of the Treaty of Versailles

**Correct Answer:** C) The assassination of Archduke Franz Ferdinand
**Explanation:** Archduke Franz Ferdinand was assassinated in Sarajevo by Gavrilo Princip, triggering the July Crisis.
**Concept Tested:** Trigger events vs. long-term structural causes."""

        elif "respiration" in prompt_lower or "executive summary" in prompt.lower():
            content = """### 📌 Executive Summary
Cellular respiration is the biochemical mechanism by which cells extract energy from glucose to synthesize ATP. It spans three stages—Glycolysis, the Krebs Cycle, and Oxidative Phosphorylation—producing ~30-32 ATP per glucose molecule.

### 🔑 Core Concepts & Key Takeaways
- **Glycolysis (Cytoplasm):** Anaerobic breakdown of 1 glucose into 2 pyruvate, generating net 2 ATP and 2 NADH.
- **Krebs Cycle (Mitochondrial Matrix):** Aerobic oxidation of Acetyl-CoA producing 2 ATP, 6 NADH, and 2 FADH2 while releasing CO2.
- **Oxidative Phosphorylation (Inner Membrane):** The electron transport chain pumps protons across cristae; ATP Synthase utilizes this electrochemical gradient to produce 26-28 ATP.

### 📖 High-Yield Terminology
- **ATP Synthase:** Rotary enzyme that synthesizes ATP driven by proton flow.
- **Chemiosmosis:** Movement of protons down their electrochemical gradient.

### ⚠️ Common Pitfalls & Tricky Distinctions
- Glycolysis is anaerobic and cytosolic; the Krebs Cycle and ETC occur in mitochondria.

### 🎯 Recommended Study Next-Step
Draw a carbon and electron flow diagram tracing glucose from cytoplasm to the electron transport chain."""

        elif "inflation" in prompt_lower or "diagnostic evaluation" in prompt.lower():
            content = """### 📊 Diagnostic Evaluation & Rubric
- **Estimated Score:** 5.5 / 10
- **Clarity & Flow:** Easy to understand, but uses colloquial phrasing ("buy stuff", "cash in pockets").
- **Factual Completeness:** Correctly identifies that more money leads to higher demand and prices, but misses aggregate supply constraints.
- **Academic Tone & Vocabulary:** Lacks formal economic terms like *Aggregate Demand*, *Purchasing Power*, and *Monetary Expansion*.

### 🔍 Strengths (What Worked Well)
- Correctly explains the intuitive relationship between excess money and rising price levels.

### ⚠️ Areas for Improvement (What was Missing or Flawed)
- Needs formal economic definitions (Aggregate Demand shifting right against fixed Aggregate Supply).
- Explain *why* suppliers raise prices instead of instantly expanding production.

### 🌟 Upgraded Model Answer
When a central bank expands the money supply faster than real economic output (GDP) grows, it induces **demand-pull inflation**. In the short term, increased liquidity raises household disposable income, shifting **Aggregate Demand (AD)** rightward. Because **Aggregate Supply (AS)** is constrained by existing capital and labor capacity, suppliers cannot instantaneously match demand, bidding price levels upwards. This sustained price increase erodes **consumer purchasing power**, reducing real living standards unless nominal wages keep pace.

### 💡 Key Writing Lesson
Always connect the **cause** (Monetary Expansion) to the **mechanism** (AD shifting faster than AS can adjust) before stating the **impact** (Erosion of Real Purchasing Power)."""

        else:
            content = """### 🎯 The Core Intuition in One Sentence
A Transformer neural network understands language by analyzing how every word in a sentence relates to every other word simultaneously, rather than reading one word at a time.

### 🍎 The Real-World Analogy
Think of a round-table conference where 10 experts talk. Instead of passing notes one by one like a telephone game (RNNs), everyone has headphones and can instantly pay **attention** to whichever speaker has the exact information they need.

### ⚙️ How It Works (Step-by-Step Breakdown)
1. **Positional Encoding:** Adds mathematical timestamps to word vectors because all words are processed in parallel.
2. **Self-Attention (Query, Key, Value):** Dynamically calculates attention scores showing how strongly words depend on each other.
3. **Feedforward Layers & Residuals:** Stacks layers of nonlinear transformations to build higher-order contextual representations.

### 🚫 The Biggest Common Misconception
Transformers are not static search databases; they are statistical probability engines computing contextual token relationships.

### 🧪 10-Second Quick Self-Check
- **Question:** Why do Transformers train faster than older RNNs?
- **Answer:** Because Self-Attention processes the entire text sequence simultaneously in parallel instead of one step at a time."""

        return AIResponse(
            success=True,
            content=content,
            error=None,
            model_used="simulated-gemini-engine (Demo Mode)",
            is_demo=True,
            duration_sec=duration
        )