## [1.3.3](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.2...v1.3.3) (2026-05-11)

### Bug Fixes

* update color scales and text formatting in horizontal bar charts ([8b6f1ef](https://github.com/MariamDouamba/water-quality-pipeline/commit/8b6f1ef1979d7e62fb497d9781060a8d51431a0e))

## [1.3.2](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.1...v1.3.2) (2026-05-11)

### Bug Fixes

* update gauge display and layout in Streamlit dashboard ([fc8235b](https://github.com/MariamDouamba/water-quality-pipeline/commit/fc8235bf42f769d6bea776b0843380b61fcd6202))

## [1.3.1](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.0...v1.3.1) (2026-05-11)

### Bug Fixes

* fallback données démo sans token ([4966eb4](https://github.com/MariamDouamba/water-quality-pipeline/commit/4966eb436043dc8d8d3574a7b39e9d457add7530))

## [1.3.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.9...v1.3.0) (2026-05-11)

### Features

* add Flask backend for AquaStat dashboard with API integration ([bce99fb](https://github.com/MariamDouamba/water-quality-pipeline/commit/bce99fb330e8fbc3b6cf48eb6221b572b49cead2))

## [1.2.9](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.8...v1.2.9) (2026-05-11)

### Bug Fixes

* add numpy dependency to requirements ([c0d9d48](https://github.com/MariamDouamba/water-quality-pipeline/commit/c0d9d48a7692bf6e4c416be21e602be5e2a1a2bf))

## [1.2.8](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.7...v1.2.8) (2026-05-11)

### Bug Fixes

* improve null value handling by replacing "NULL", "nan", and empty strings with true nulls ([ec1fcb3](https://github.com/MariamDouamba/water-quality-pipeline/commit/ec1fcb371c887a4b62e805f03e357336e224d186))

## [1.2.7](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.6...v1.2.7) (2026-05-11)

### Bug Fixes

* remove unnecessary caching for data loading in Silver transformations ([d749684](https://github.com/MariamDouamba/water-quality-pipeline/commit/d7496848c2738ea0f96e35de1afe7a8013a1274f))

## [1.2.6](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.5...v1.2.6) (2026-05-11)

### Bug Fixes

* optimize data ingestion by writing chunks directly to Delta and improve caching in Silver transformations ([96994d3](https://github.com/MariamDouamba/water-quality-pipeline/commit/96994d3e915f2034374dc65122949100e2ec3b86))

## [1.2.5](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.4...v1.2.5) (2026-05-11)

### Bug Fixes

* optimize CSV reading by eliminating intermediate file writes and improving data ingestion ([83dd58e](https://github.com/MariamDouamba/water-quality-pipeline/commit/83dd58eabbf62d01e446a0b71d2087cb1ec7abe8))

## [1.2.4](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.3...v1.2.4) (2026-05-11)

### Bug Fixes

* enhance error handling and improve CSV download process ([6df6b3b](https://github.com/MariamDouamba/water-quality-pipeline/commit/6df6b3b849f8baa58f7e2ee247fd292ac9941307))

## [1.2.3](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.2...v1.2.3) (2026-05-10)

### Bug Fixes

* implement chunked CSV reading and writing for improved data ingestion ([b01c5af](https://github.com/MariamDouamba/water-quality-pipeline/commit/b01c5af4d504d4164a68a381f4590e2f3f6e082f))

## [1.2.2](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.1...v1.2.2) (2026-05-09)

## [1.2.1](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.2.0...v1.2.1) (2026-05-09)

### Bug Fixes

* implement chunked CSV writing and Spark reading for data ingestion ([f6aec8c](https://github.com/MariamDouamba/water-quality-pipeline/commit/f6aec8cc11e39d3855f4555b3cc3380775583fe8))

## [1.2.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.1.1...v1.2.0) (2026-05-09)

### Features

* add deployment job to sync Databricks repositories ([790554a](https://github.com/MariamDouamba/water-quality-pipeline/commit/790554ad4db7bf90c134506c40f0b776d8e091de))

## [1.1.1](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.1.0...v1.1.1) (2026-05-09)

### Bug Fixes

* use Pandas to Spark conversion instead of CSV files ([dc942f7](https://github.com/MariamDouamba/water-quality-pipeline/commit/dc942f712c06cd79dd9938154234efa67a613057))

## [1.1.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.0.0...v1.1.0) (2026-05-07)

### Features

* add CSV export endpoints for departments and non-conformities, and implement semantic release configuration ([c82f3b1](https://github.com/MariamDouamba/water-quality-pipeline/commit/c82f3b156e4ec743fd9fc02d1041d58088f7f27a))
