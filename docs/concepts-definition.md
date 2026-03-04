# Output Density Matters

In 2026, we measure two main types of speed:

- **TTFT (Time to First Token)**: How fast the model starts talking.
- **TPOT (Time Per Output Token)**: How fast it finishes the sentence.

Your Summarize result (25s) likely had a high TTFT because it had to read the Rayleigh scattering text first. Your Math result had a low TTFT because the input was tiny.

## Detailed Definitions

### TTFT (Time to First Token)
TTFT measures the latency from the moment a prompt is sent to the model until the first token of the response is generated and returned. This is the "time to start talking" – it reflects how quickly the model begins processing and outputting.

**Why it matters**: TTFT is crucial for user experience, especially in interactive applications where quick responses are expected. A high TTFT can make the system feel slow, even if the overall throughput is good.

**Factors affecting TTFT**:
- Input prompt length: Longer prompts require more processing time.
- Model size and complexity: Larger models may have higher initial latency.
- Hardware and optimization: Faster GPUs or optimized inference can reduce TTFT.
- Caching and pre-processing: Systems with prompt caching can lower TTFT for repeated or similar inputs.

### TPOT (Time Per Output Token)
TPOT measures the average time taken to generate each token after the first one. It represents the throughput or "speed of finishing the sentence" – how efficiently the model produces subsequent tokens.

**Why it matters**: TPOT affects the overall time for long responses. Lower TPOT means faster completion of outputs, which is important for tasks requiring detailed or lengthy replies.

**Factors affecting TPOT**:
- Output length: Longer outputs may have varying TPOT due to diminishing returns or context accumulation.
- Model efficiency: Well-optimized models have lower TPOT.
- Hardware parallelism: Better parallel processing can improve token generation speed.
- Context size: As the conversation history grows, TPOT might increase due to larger context.

## Future Concepts
This document will be expanded with more speed and efficiency metrics as they become relevant in LLM evaluation.
