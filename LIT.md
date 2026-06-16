# Source Literature Notes

## Core Topic

Automated image quality classification for Siberian Radioheliograph (SRH) solar radio images using an ensemble of deep learning models. The paper develops a method to classify SRH images as "GOOD" or "BAD" quality to filter low-quality data from the SRH catalog.

**Source:** Egorov, Y. (2025). Siberian radioheliograph image classification using ensemble of CLIP, EfficientNet and CatBoost models. arXiv:2507.04211v1 [astro-ph.SR].

## Key Findings

1. Zero-shot CLIP model was used to automatically label 100,000 images from the SRH catalog into "GOOD"/"BAD" classes using text cues ("photo of a circle" for GOOD, "photo of noise" for BAD), with manual validation of 10,000 images.
2. Four models were evaluated: fine-tuned EfficientNet B0, CatBoost with CLIP embeddings, CatBoost with EfficientNet embeddings, and an Ensemble model (feedforward neural network combining all three predictions).
3. The Ensemble model achieved the best performance with **95% accuracy**, outperforming individual models (EfficientNet: ~90%, CLIP+CatBoost: ~92%, EfficientNet+CatBoost: ~95%).
4. A daily classification service was deployed at https://forecasting.iszf.irk.ru/srh with a RESTful API and Python/IDL client examples.
5. SRH catalog contains 100,000+ radio images (3-24 GHz) since August 2021 with ~2 min cadence; calibration uses redundancy-based method and CLEAN algorithm.

## Extracted Keywords

- Sun · Radio emission · Radio telescopes · Siberian radioheliograph (SRH)
- Transfer learning · EfficientNet · CLIP · CatBoost · Ensemble model
- Image classification · Deep learning · Solar physics · Space weather
- Image quality assessment · Radio interferometry · CLEAN algorithm
- F10.7 index · Solar radio bursts · Solar-Terrestrial Physics
