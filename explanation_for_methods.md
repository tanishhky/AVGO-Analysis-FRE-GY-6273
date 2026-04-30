
---

# 1. Discounted Cash Flow (DCF)

**The core idea:** A company is worth the present value of all the cash it will generate for shareholders, from now until the end of time.

**The procedure:**
1. Forecast Free Cash Flow to the Firm (FCFF) for an explicit period — usually 5 or 10 years. FCFF = EBIT × (1 − tax rate) + D&A − Capex − ΔWorking Capital.
2. Estimate a terminal value at the end of the explicit period using either Gordon Growth (TV = FCFF × (1+g) / (WACC − g)) or an exit multiple.
3. Discount everything back to today using WACC.
4. Add cash, subtract debt, divide by share count → equity value per share.

**WACC is the discount rate** — it's the blended cost of equity and debt. For Broadcom we got 9.38%:
- Cost of equity = Rf + β × ERP = 4.31% + 1.20 × 5.0% = 10.31%
- Cost of debt (after-tax) = 5.0% × (1 − 0.18) = 4.10%
- WACC = 0.85 × 10.31% + 0.15 × 4.10% = 9.38%

**The reasoning:** It's the most theoretically defensible method because it values a company on its actual cash-generating ability, not on what other companies happen to trade at. Warren Buffett famously says "intrinsic value is the discounted value of all future cash" — that's literally what DCF computes.

**Ideal for:**
- **Mature, predictable businesses** with stable cash flows (utilities, consumer staples, mature industrials)
- **Companies you can reasonably forecast 5+ years out** — established business model, predictable margins
- **Capital-intensive businesses** where capex and working capital matter

**Weaknesses:**
- **Garbage in, garbage out.** Your forecast is a guess. Small changes in WACC or terminal growth swing the answer by 30%+.
- **Terminal value is usually 70-80% of total value.** For Broadcom, it's 80%. That means we're really valuing what happens *after* our forecast, which is the part we know least about.
- **Doesn't work for early-stage companies** (negative FCF), bank/insurance (different cash flow structure), or anything in genuine disruption.

**Why it works for AVGO:** Broadcom has stable, high-margin cash flow ($27B FCF on $64B revenue — 42% conversion). The challenge is that the AI segment is in a high-growth phase, which is why we lean on the other three methods to triangulate.

---

# 2. Sum-of-the-Parts (SOTP)

**The core idea:** A conglomerate of multiple businesses should be valued segment by segment, applying each segment's appropriate multiple, then summed. The whole equals the sum of the parts.

**The procedure:**
1. Split the company into reporting segments (Broadcom: Semi vs Software).
2. For each segment, find pure-play public comparables. For Semi, that's NVDA, AMD, MRVL. For Software, that's mature SaaS companies.
3. Apply the peer-group multiple to that segment's metric (we used FY27E EBITDA × peer EV/EBITDA multiple).
4. Sum the segment EVs, subtract net debt, divide by shares → implied price.

For Broadcom: Semi $82B EBITDA × 20x = $1.64T. Software $24B × 17x = $0.41T. Total EV ~$2.05T → ~$401 per share.

**The reasoning:** Different businesses have different risk profiles and different multiples. Mature mainframe software trades at 12x EBITDA; high-growth AI silicon trades at 25x+. If you apply one blended multiple to the whole company, you systematically misvalue both segments. SOTP fixes this.

**Ideal for:**
- **Conglomerates with structurally different segments** (Berkshire Hathaway, GE before the breakup, AVGO)
- **Companies that have done large M&A** combining different industries (Broadcom + VMware is a textbook case)
- **When activist investors call for a "breakup"** — SOTP tells you what the breakup value would be

**Weaknesses:**
- **Pure-play comps don't really exist.** What's the right peer for VMware Cloud Foundation? Is it Microsoft Azure? ServiceNow? The choice changes the answer by 20%+.
- **You need segment financial disclosure** at a level companies often don't provide (segment EBITDA margins, segment capex).
- **Conglomerate discount problem.** Even after computing SOTP, conglomerates often trade at a 10-20% discount to the sum because investors don't trust complex structures.

**Why it works for AVGO:** Broadcom is genuinely two distinct businesses bolted together by Hock Tan's M&A playbook. The Semi business should NOT trade at the same multiple as enterprise software, and the market knows it. SOTP gives you the breakup value as a sanity check.

---

# 3. Trading Comparables ("Comps")

**The core idea:** Similar companies should trade at similar multiples. Find peers, look at what they trade at, apply that to your target.

**The procedure:**
1. Identify 5-10 peer companies (we used NVDA, AMD, MRVL, QCOM, TXN, INTC, TSM).
2. Compute their valuation multiples — most commonly:
   - **Forward P/E** (price ÷ next-year EPS)
   - **EV/EBITDA** (enterprise value ÷ EBITDA)
   - **EV/Sales**
   - **PEG ratio** (P/E ÷ growth rate)
3. Take the median or mean of the peer set.
4. Apply that multiple to the target's corresponding metric.

For Broadcom: peer median Forward P/E is 25.6x. We applied a more conservative 22x to our $20.00 CY27 EPS estimate → $440 per share.

**The reasoning:** This is the "market test." If the market is pricing AVGO's peers at 25x earnings, it's pricing the *risks and growth* of that industry. Trading comps tell you what someone is actually willing to pay, today, for similar businesses.

**Ideal for:**
- **Mature industries with many comparable public companies** (semis, banks, REITs, oil & gas)
- **Quick reality checks** on a DCF — if your DCF says $800 but peers trade at 15x and your math implies 50x, something is off
- **IPO pricing** — banks live and die by comps when pricing new offerings
- **M&A** — what would an acquirer pay?

**Weaknesses:**
- **No two companies are truly comparable.** Is NVDA really a peer for AVGO? They sell different products to overlapping customers. AMD has higher growth than AVGO but trades at 80x EV/EBITDA — does that mean AVGO is undervalued or AMD is overvalued?
- **Multiple expansion/contraction is endogenous.** During the 2021 SPAC bubble, every tech "peer" traded at 30x sales. By 2023 they were at 8x. Your comps answer changes wildly with sentiment.
- **It tells you what the market thinks, not what something is worth.** If the market is wrong about the whole sector (think 1999 dotcoms), comps are wrong with it.

**Why it works for AVGO:** Semis is one of the most well-comped sectors in equity research. Every analyst tracks the same 8-10 names. The peer multiples are real and observable. The trick — which we did — is choosing *conservative* multiples (22x P/E vs peer median 25.6x) so you're not just rubber-stamping the market.

---

# 4. Monte Carlo Simulation

This is the one you said wasn't clear, so let me build it from scratch.

## The problem Monte Carlo solves

Every valuation method above gives you **one number**. DCF says $436. SOTP says $401. Comps say $440.

But every one of those numbers depends on **assumptions** — and every assumption could be wrong.

For example, our DCF assumes FY27 AI revenue = $115B. What if it's $90B? What if it's $150B? Each scenario gives a totally different price.

You could run a "sensitivity table" — that's what the WACC × terminal-growth heatmap on slide 8 is. But sensitivity tables only let you vary 2 inputs at a time. Real life has 5 or 10 things that could go wrong simultaneously.

**Monte Carlo lets you vary ALL the assumptions at once, randomly, thousands of times, to see the full distribution of possible outcomes.**

## The intuition (analogy)

Imagine you're trying to estimate how long your commute home will take.

**The DCF approach:** You assume average traffic, average weather, average lights. You compute: 35 minutes. Done.

**The sensitivity table approach:** You compute four scenarios — traffic light/heavy × weather good/bad. You get: 25, 35, 40, 55 minutes.

**The Monte Carlo approach:** You list every variable that affects commute time:
- Traffic density (could be 0.5x to 2x normal)
- Number of red lights hit (could be 5 to 20)
- Weather penalty (0% to 30% slowdown)
- Random delays (accident, construction)
- Your own driving variability

Then you simulate 10,000 commutes by **drawing each variable randomly from its plausible range** and computing the resulting time. You end up with 10,000 outcomes. You plot them as a histogram.

What you learn:
- Median commute: 35 minutes (matches the deterministic answer)
- 25th percentile: 28 minutes
- 75th percentile: 45 minutes
- 95th percentile (bad day): 75 minutes
- Probability of being late if you must arrive in 40 minutes: 35%

That last number is what makes Monte Carlo valuable. **You get probabilities, not point estimates.**

## How we did it for Broadcom

We identified 6 key inputs to the valuation, and assigned each a **probability distribution** instead of a single number:

| Input | Distribution | Why this distribution |
|---|---|---|
| FY27 AI revenue | Normal(mean=$125B, sd=$25B) | Street midpoint with the dispersion analyst range implies |
| AI growth post-FY27 | Normal(mean=30%, sd=10%) | Reflects uncertainty about how long AI ramp lasts |
| Terminal growth | Normal(mean=3.0%, sd=0.5%) | Centered on long-run GDP growth |
| WACC | Normal(mean=9.38%, sd=0.5%) | Sensitive to rates, which move |
| Steady-state EBITDA margin | Normal(mean=68.5%, sd=2.5%) | Reflects mix-shift uncertainty |
| Capex/Sales | Normal(mean=1.1%, sd=0.3%) | Capital intensity could rise with rack-scale |

Then the algorithm runs 10,000 times. Each iteration:

1. Draw a random value for each of the 6 inputs from its distribution. Example draw: AI revenue = $138B, growth = 27%, terminal = 2.8%, WACC = 9.6%, margin = 67%, capex = 1.2%.
2. Plug those into the DCF model.
3. Compute the implied per-share price for THIS draw.
4. Save the result.
5. Repeat 9,999 more times.

You end up with 10,000 implied prices. Histogram them — that's Figure 10 in the report.

## What the Monte Carlo output tells you

Looking at our Broadcom result:
- **Mean: $471.** Average across all 10,000 simulated futures.
- **Median: $456.** Middle outcome — half of simulations are above, half below.
- **P25: $378.** 25% of simulations land below $378 (this is your "fairly bad" case).
- **P75: $544.** 75% of simulations land below $544 (this is your "fairly good" case).
- **P5: $287.** 5% of simulations land below $287 (genuine bear case).
- **P95: $711.** 5% of simulations land above $711 (genuine bull case).
- **Prob > spot: 68.3%.** In 6,830 of our 10,000 simulations, intrinsic value came out above $399.83. So if you bought at $400 today, in roughly 2 out of 3 plausible futures, the stock is worth more than what you paid.

That last number is what supports the BUY rating.

## Why Monte Carlo is powerful for Broadcom specifically

- **Multiple things could go right (or wrong) at the same time.** AI revenue could disappoint AND WACC could rise AND margin could compress. A single sensitivity table can't show you the joint probability of these things.
- **The distribution is asymmetric.** Look at the histogram — the right tail is fatter than the left. That's because Broadcom has more upside optionality (FY27 AI could surprise to $150B+) than symmetric downside. A point-estimate DCF hides this; a Monte Carlo shows it.
- **It frames the bet probabilistically.** Instead of saying "the stock is worth $456 so buy below that," we say "two-thirds of plausible futures support a price above $400." The second framing is much more honest about uncertainty.

## Procedure summary (if a prof asks)

1. **Identify the key inputs** that drive your DCF and that have meaningful uncertainty.
2. **Assign a probability distribution to each** — Normal is most common, but you can use Lognormal, Uniform, Triangular, or empirical depending on the variable.
3. **Run N simulations** (we used 10,000; for a research report 5K-10K is standard, for a real institutional model 100K+ is common).
4. **For each simulation, draw one value from each input distribution** (independently — though you can also model correlations).
5. **Compute the output (price) under that draw** by running the full valuation model.
6. **Aggregate the outputs** as a distribution.
7. **Report key statistics:** mean, median, percentiles, and probability of crossing key thresholds.

## Ideal for:

- **High-uncertainty businesses** (AI, biotech, early-stage tech, anything in disruption)
- **Companies with multiple distinct value drivers** (a conglomerate, a multi-product platform)
- **When you need a probability statement** ("what's the chance this is worth more than $X?") — required for risk-adjusted decision-making
- **Real options analysis** — projects that have value because of optionality

## Weaknesses

- **You're still making up the input distributions.** If you assume FY27 AI is ~ N($125B, $25B), the answer depends entirely on whether that's the right distribution. Garbage in, garbage out — same as DCF.
- **It assumes inputs are independent (or you have to model the correlations).** In reality, if AI revenue disappoints, margin probably compresses too — they're correlated. Pure independent sampling overstates the spread.
- **It can give a false sense of precision.** "There's a 68.3% probability of upside" sounds rigorous, but the precision is fake — change FY27 AI mean to $120B and the probability is 62%; change it to $130B and it's 73%. The number depends entirely on your subjective input choices.
- **Black swans not captured.** Normal distributions have thin tails. A real "AI bubble pops" scenario isn't a 5-sigma event in our N($125B, $25B) — it's outside the distribution we assumed. Monte Carlo is useless against the unknown unknowns.

---

# How they fit together

Each method answers a slightly different question:

| Method | Answers |
|---|---|
| DCF | What is this worth based on its own cash flows? |
| SOTP | What is this worth if we broke it up and sold the pieces? |
| Comps | What is the market currently paying for similar businesses? |
| Monte Carlo | What is the *distribution* of plausible outcomes given uncertainty? |

That's why we use four methods. DCF gives the "fundamental" answer, SOTP gives the "structural" answer, comps give the "market" answer, and Monte Carlo gives the "probabilistic" answer. When all four cluster in the same range — $400-510 in our case — you have high confidence in the recommendation.

# Likely Q&A questions on these methods specifically

**"Why didn't you do a dividend discount model?"** AVGO has a 0.79% yield — too small for DDM to be meaningful. DDM works for utilities, REITs, and dividend aristocrats where the dividend is the bulk of return.

**"Why didn't you do a residual income or EVA model?"** Could have. EVA would tell us whether AVGO is creating value above its cost of capital. Spoiler: yes, by a lot. Didn't add new info given the DCF.

**"Why didn't you use a Lognormal for FY27 AI revenue instead of Normal?"** Good catch. Lognormal would prevent negative draws (which Normal doesn't, though our mean/sd combination makes this rare). For a real institutional model we'd use Lognormal. For a 10K-path simulation with mean $125B / sd $25B, the probability of drawing a negative is 0.000003% — negligible.

**"Did you correlate your inputs?"** No, all inputs are independently drawn. That's a known simplification — in reality, AI revenue and EBITDA margin would be positively correlated (operating leverage). Modeling that correctly would *narrow* our distribution somewhat, which would actually strengthen the BUY thesis.

**"What's the difference between Monte Carlo and a tornado chart?"** Tornado is one-variable-at-a-time (univariate sensitivity). Monte Carlo is all-variables-at-once (multivariate). Tornado tells you which input matters most in isolation; Monte Carlo tells you the full joint distribution.
