# Saharasoil — 360° Investor Dashboard

A live, formula-driven investor dashboard built on `Saharasoil_B2B_Model_Reanchored.xlsx` and
everything else generated for the pitch (proposal, TAM/SAM/SOM, roadmap, risk register, unit
economics). Every chart recalculates when you move a slider — nothing on screen is a hardcoded
picture of a spreadsheet.

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud (free)

1. Push this folder (`app.py`, `model_engine.py`, `requirements.txt`) to a GitHub repo.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub.
3. Click **New app**, pick the repo, set the main file to `app.py`, click **Deploy**.
4. You'll get a public `*.streamlit.app` link you can put directly on a slide or send to the panel.

## What's inside

- **`model_engine.py`** — the calculation engine, kept separate from the UI on purpose so the
  numbers can be unit-tested. Running `python model_engine.py` directly checks every output
  against the source workbook's validated figures.
- **`app.py`** — the Streamlit UI: 8 tabs (Overview, Product 360°, Market Sizing, Unit Economics,
  Financial Model, Risk Register, Roadmap, The Ask), a sidebar of live model controls, and a
  consistent navy/sand/rust visual identity matching the rest of the pitch materials.

## A correction made along the way

The uploaded workbook's `Gross profit / contractor` formula used the top-dressing **COGS%**
where it should have used the top-dressing **margin%**. That understated gross profit per
contractor (AED 2,532 instead of AED 2,748) and, downstream, understated LTV and LTV:CAC while
overstating the break-even contractor count. This dashboard uses the corrected formula — it's
flagged transparently inside the **Unit Economics** tab under "Methodology note" so it can be
explained confidently if asked.

## Presenting live

- The sidebar sliders are the whole point: if a judge asks "what if tonnes-per-contractor is
  only 4, not 6?" — move the slider, live, in front of them. The Risk Register tab's
  Demand-Side Risk section exists specifically to invite that question rather than hide from it.
- Use **Reset to validated defaults** to snap back to the pitch-ready baseline before/after any
  live "what-if" exploration.
