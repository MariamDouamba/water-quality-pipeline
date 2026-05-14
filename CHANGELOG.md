## 1.0.0 (2026-05-14)

### Features

* add bronze ingestion notebook ([48c7963](https://github.com/MariamDouamba/water-quality-pipeline/commit/48c79636604f00c8261e8340e5649c52a77652c6))
* add CSV export endpoints for departments and non-conformities, and implement semantic release configuration ([e801bc9](https://github.com/MariamDouamba/water-quality-pipeline/commit/e801bc9882a9243a9910357422db7212621a72d8))
* add deployment job to sync Databricks repositories ([568057f](https://github.com/MariamDouamba/water-quality-pipeline/commit/568057f42300d8a03e9a870e1d8eef56262ff461))
* add FastAPI to expose gold layer data ([35a3b78](https://github.com/MariamDouamba/water-quality-pipeline/commit/35a3b783fa4b883d6ba647f593aabe9664cbdfe7))
* add Flask backend for AquaStat dashboard with API integration ([cfcc6cd](https://github.com/MariamDouamba/water-quality-pipeline/commit/cfcc6cd5ada7af5651ac77e183aef8f765d9252a))
* add gold star schema notebook ([e0a6b99](https://github.com/MariamDouamba/water-quality-pipeline/commit/e0a6b991268d4404275fe816cf9c9c85328397e7))
* add Great Expectations quality checks notebook ([6d4ee60](https://github.com/MariamDouamba/water-quality-pipeline/commit/6d4ee60ca5090635e47b1c56805588ae70651f26))
* add pipeline configuration ([2903dd3](https://github.com/MariamDouamba/water-quality-pipeline/commit/2903dd3f99cafd9855759e3c17dcda9e78acf129))
* add silver transformation notebook ([3c6df73](https://github.com/MariamDouamba/water-quality-pipeline/commit/3c6df73a3697ffdbaa516be2b368f73b9eb8787a))
* add Unity Catalog setup notebook and API structure ([baf123d](https://github.com/MariamDouamba/water-quality-pipeline/commit/baf123d6a30a76cb0ff88290ac154cc51d78cedf))
* **dashboard:** 10 améliorations — palette eau, UX, données ([a68fde8](https://github.com/MariamDouamba/water-quality-pipeline/commit/a68fde81ba8243023959db7ee8ac3481bbf11c15))
* **dashboard:** editorial redesign inspired by Hydrographe aesthetic ([703d51b](https://github.com/MariamDouamba/water-quality-pipeline/commit/703d51bf61cde293afa1a5cc8c16f27a1b51ec88)), closes [#c77b5a](https://github.com/MariamDouamba/water-quality-pipeline/issues/c77b5a) [#0c0e12](https://github.com/MariamDouamba/water-quality-pipeline/issues/0c0e12)
* **dashboard:** interactive dept click + 6 live KPIs ([5fe8c82](https://github.com/MariamDouamba/water-quality-pipeline/commit/5fe8c8202d4eea32a6270383ae28e412f3b50590))
* **dashboard:** original AquaStat identity — teal/amber palette, Space Grotesk + JetBrains Mono ([616844a](https://github.com/MariamDouamba/water-quality-pipeline/commit/616844aed09c926a05aecf1d7a2649844f656780)), closes [#050f0f](https://github.com/MariamDouamba/water-quality-pipeline/issues/050f0f) [#00cfb4](https://github.com/MariamDouamba/water-quality-pipeline/issues/00cfb4) [#e8b86d](https://github.com/MariamDouamba/water-quality-pipeline/issues/e8b86d) [#e05c5c](https://github.com/MariamDouamba/water-quality-pipeline/issues/e05c5c)
* **dashboard:** palette eau profonde — azur/amber remplace teal/vert ([3968bac](https://github.com/MariamDouamba/water-quality-pipeline/commit/3968bacf8ec2de22a4418c2dd06ebbfacf21f261)), closes [#040c18](https://github.com/MariamDouamba/water-quality-pipeline/issues/040c18) [#38b2f8](https://github.com/MariamDouamba/water-quality-pipeline/issues/38b2f8) [1565c0/#5b8dd9](https://github.com/1565c0/water-quality-pipeline/issues/5b8dd9) [#e8b86d](https://github.com/MariamDouamba/water-quality-pipeline/issues/e8b86d)
* **dashboard:** redesign with choropleth map, live KPIs, and fixed filters ([791a7a4](https://github.com/MariamDouamba/water-quality-pipeline/commit/791a7a45a08ef9f2c8aac8605023b36eea8b2595))
* **dashboard:** remplace 9 indicateurs statiques par analyse communes ([a35abc4](https://github.com/MariamDouamba/water-quality-pipeline/commit/a35abc49d6af85cb953a0c97f333afc656d6fc28))
* implement FastAPI for water quality data API with endpoints and Pydantic models ([79e8c50](https://github.com/MariamDouamba/water-quality-pipeline/commit/79e8c50a74ffc2b17aee2fde4c23dcbcb4733b4c))
* ingest all 3 source files (results, samples, communes) ([5228be8](https://github.com/MariamDouamba/water-quality-pipeline/commit/5228be8bf0443138d041b3167150a5aadec7d447))
* update config with 3 sources and 8 tables ([32673d3](https://github.com/MariamDouamba/water-quality-pipeline/commit/32673d3a6bc485b27e514a17071c7e5d8a9f6223))
* update gold with 6 dimensions and enriched star schema ([1a5934e](https://github.com/MariamDouamba/water-quality-pipeline/commit/1a5934e11e079a1971bf2d6a37935ff24caf5558))
* update silver with dates, communes and full classification ([80904f0](https://github.com/MariamDouamba/water-quality-pipeline/commit/80904f059063b38e66d932f347e3d15c0f356e0b))

### Bug Fixes

* add error logging for Databricks connection failures ([91de8cd](https://github.com/MariamDouamba/water-quality-pipeline/commit/91de8cdecb9693bcd2d0bbd1d77b4ea1f44c58e5))
* add numpy dependency to requirements ([67913ae](https://github.com/MariamDouamba/water-quality-pipeline/commit/67913ae89af4f7ba04c80f0b25d3412932c742ee))
* charts Plotly + connexion Databricks via st.secrets ([94fe2ef](https://github.com/MariamDouamba/water-quality-pipeline/commit/94fe2efd4d753441f29d2bfdfde90169f3131dc5))
* **dashboard:** contrast & map readability ([de4e94b](https://github.com/MariamDouamba/water-quality-pipeline/commit/de4e94bebf7db4dd7c0f4d08fabc2202d14f1b9a)), closes [#2a4a47](https://github.com/MariamDouamba/water-quality-pipeline/issues/2a4a47) [#4a9990](https://github.com/MariamDouamba/water-quality-pipeline/issues/4a9990)
* **dashboard:** correct taux_conformite — exclude Non evalue from denominator ([8b56f97](https://github.com/MariamDouamba/water-quality-pipeline/commit/8b56f97a1daa581053c5ef909fc25999344e80ac))
* **dashboard:** fix all remaining low-contrast colors and gauge range ([062ef54](https://github.com/MariamDouamba/water-quality-pipeline/commit/062ef54d369720710ce8a218e22dcd102dbde629)), closes [#2a4a47](https://github.com/MariamDouamba/water-quality-pipeline/issues/2a4a47) [#1a3330](https://github.com/MariamDouamba/water-quality-pipeline/issues/1a3330) [#4a9990](https://github.com/MariamDouamba/water-quality-pipeline/issues/4a9990) [#3a7070](https://github.com/MariamDouamba/water-quality-pipeline/issues/3a7070) [#00cfb4](https://github.com/MariamDouamba/water-quality-pipeline/issues/00cfb4) [#4a9990](https://github.com/MariamDouamba/water-quality-pipeline/issues/4a9990)
* enhance error handling and improve CSV download process ([8240edc](https://github.com/MariamDouamba/water-quality-pipeline/commit/8240edc9990be31e87f1aac6b72e7842b2029f2f))
* enhance error logging for Databricks credentials retrieval ([1b961df](https://github.com/MariamDouamba/water-quality-pipeline/commit/1b961df57ea48e05f480ba472637012378c0b3a9))
* fallback données démo sans token ([ad5e0ac](https://github.com/MariamDouamba/water-quality-pipeline/commit/ad5e0ac70e503ebea5a575d2735d08d8ccd64929))
* force redeploy Streamlit Cloud ([9ac5982](https://github.com/MariamDouamba/water-quality-pipeline/commit/9ac5982424500d2d9b5a4b6fa17b4b2b27958b6c))
* implement chunked CSV reading and writing for improved data ingestion ([2fac95e](https://github.com/MariamDouamba/water-quality-pipeline/commit/2fac95e4d81bd90e7ed1080d7c75d84650f3ece8))
* implement chunked CSV writing and Spark reading for data ingestion ([dc56307](https://github.com/MariamDouamba/water-quality-pipeline/commit/dc56307b64d46530b00b15a4697d3879b329c7a1))
* improve null value handling by replacing "NULL", "nan", and empty strings with true nulls ([3e0c18e](https://github.com/MariamDouamba/water-quality-pipeline/commit/3e0c18e8789d358e68a8b9d62e20b5079736ca5d))
* optimize CSV reading by eliminating intermediate file writes and improving data ingestion ([211b36f](https://github.com/MariamDouamba/water-quality-pipeline/commit/211b36f2d7d5700717ae365f456c4dc3071de7c1))
* optimize data ingestion by writing chunks directly to Delta and improve caching in Silver transformations ([689e46a](https://github.com/MariamDouamba/water-quality-pipeline/commit/689e46a82a7bb789e78216f20b3bb7a4a1ef9730))
* refactor Databricks connection to use context manager for better resource handling ([0fb0ea2](https://github.com/MariamDouamba/water-quality-pipeline/commit/0fb0ea2d021cf2ed710618e0976de474e76d154a))
* remove unnecessary caching for data loading in Silver transformations ([330319f](https://github.com/MariamDouamba/water-quality-pipeline/commit/330319f818056687ebb44a3c9d39f3a2f69f8e1d))
* simplify CI workflow ([a9ae1cd](https://github.com/MariamDouamba/water-quality-pipeline/commit/a9ae1cdf2122dc84b174ffd99cfa3cb0383c5479))
* suppression marker_line_color + use_container_width deprecated ([e563dc7](https://github.com/MariamDouamba/water-quality-pipeline/commit/e563dc7f79b08784292aeea6e3674534ec0b27d8))
* update CI to expect 10 tables ([28f1097](https://github.com/MariamDouamba/water-quality-pipeline/commit/28f1097c940738c1b5f60d658a899381dd59930f))
* update color scales and text formatting in horizontal bar charts ([4c44836](https://github.com/MariamDouamba/water-quality-pipeline/commit/4c44836e5d2f38b794f64498f02a9ccbcd20a8ee))
* update fastapi version constraint to allow newer releases ([63cfbe6](https://github.com/MariamDouamba/water-quality-pipeline/commit/63cfbe6f39b937677740d5551d01ef8047a3403d))
* update gauge display and layout in Streamlit dashboard ([362621f](https://github.com/MariamDouamba/water-quality-pipeline/commit/362621f651d27214dabedb5d54c517d462d47dc4))
* update SQL queries for data retrieval and improve filtering conditions ([09f06f0](https://github.com/MariamDouamba/water-quality-pipeline/commit/09f06f0e5656ccc6d9596a5a1758e331e95fe120))
* update workspace directory path for CSV output ingestion ([bae4cdf](https://github.com/MariamDouamba/water-quality-pipeline/commit/bae4cdfd350bb500609207b4593916a1ed62d899))
* use Pandas to Spark conversion instead of CSV files ([5948c83](https://github.com/MariamDouamba/water-quality-pipeline/commit/5948c83686e2adb71f1d797f26f24f80014370e5))

## [1.10.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.9.0...v1.10.0) (2026-05-14)

### Features

* **dashboard:** remplace 9 indicateurs statiques par analyse communes ([7894cc2](https://github.com/MariamDouamba/water-quality-pipeline/commit/7894cc21981e4dc4e07d680de709cbd132e67b1e))

## [1.9.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.8.0...v1.9.0) (2026-05-14)

### Features

* **dashboard:** 10 améliorations — palette eau, UX, données ([8b22978](https://github.com/MariamDouamba/water-quality-pipeline/commit/8b22978ab3c045dbf0d96a80b776021dfccfc86d))

## [1.8.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.7.0...v1.8.0) (2026-05-14)

### Features

* **dashboard:** palette eau profonde — azur/amber remplace teal/vert ([57b2789](https://github.com/MariamDouamba/water-quality-pipeline/commit/57b27893074fef077f1f093cc078de735fb7c445)), closes [#040c18](https://github.com/MariamDouamba/water-quality-pipeline/issues/040c18) [#38b2f8](https://github.com/MariamDouamba/water-quality-pipeline/issues/38b2f8) [1565c0/#5b8dd9](https://github.com/1565c0/water-quality-pipeline/issues/5b8dd9) [#e8b86d](https://github.com/MariamDouamba/water-quality-pipeline/issues/e8b86d)

## [1.7.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.6.3...v1.7.0) (2026-05-14)

### Features

* **dashboard:** interactive dept click + 6 live KPIs ([58b1517](https://github.com/MariamDouamba/water-quality-pipeline/commit/58b1517e8012cc0b7c09d56bf3e997e9b7aa1feb))

## [1.6.3](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.6.2...v1.6.3) (2026-05-13)

### Bug Fixes

* **dashboard:** correct taux_conformite — exclude Non evalue from denominator ([921844c](https://github.com/MariamDouamba/water-quality-pipeline/commit/921844c48c91c9133df4189ba093283fdb2a0f63))

## [1.6.2](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.6.1...v1.6.2) (2026-05-13)

### Bug Fixes

* **dashboard:** fix all remaining low-contrast colors and gauge range ([4348b66](https://github.com/MariamDouamba/water-quality-pipeline/commit/4348b66afff11b2eda36d0201ce60701c1711815)), closes [#2a4a47](https://github.com/MariamDouamba/water-quality-pipeline/issues/2a4a47) [#1a3330](https://github.com/MariamDouamba/water-quality-pipeline/issues/1a3330) [#4a9990](https://github.com/MariamDouamba/water-quality-pipeline/issues/4a9990) [#3a7070](https://github.com/MariamDouamba/water-quality-pipeline/issues/3a7070) [#00cfb4](https://github.com/MariamDouamba/water-quality-pipeline/issues/00cfb4) [#4a9990](https://github.com/MariamDouamba/water-quality-pipeline/issues/4a9990)

## [1.6.1](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.6.0...v1.6.1) (2026-05-13)

### Bug Fixes

* **dashboard:** contrast & map readability ([00dd6d8](https://github.com/MariamDouamba/water-quality-pipeline/commit/00dd6d84ab18f82e6a2258505db6d398b39e9acf)), closes [#2a4a47](https://github.com/MariamDouamba/water-quality-pipeline/issues/2a4a47) [#4a9990](https://github.com/MariamDouamba/water-quality-pipeline/issues/4a9990)

## [1.6.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.5.0...v1.6.0) (2026-05-12)

### Features

* **dashboard:** original AquaStat identity — teal/amber palette, Space Grotesk + JetBrains Mono ([f5f49c3](https://github.com/MariamDouamba/water-quality-pipeline/commit/f5f49c388d6bd4d190071b0d7e80b8701d191ec2)), closes [#050f0f](https://github.com/MariamDouamba/water-quality-pipeline/issues/050f0f) [#00cfb4](https://github.com/MariamDouamba/water-quality-pipeline/issues/00cfb4) [#e8b86d](https://github.com/MariamDouamba/water-quality-pipeline/issues/e8b86d) [#e05c5c](https://github.com/MariamDouamba/water-quality-pipeline/issues/e05c5c)

## [1.5.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.4.0...v1.5.0) (2026-05-12)

### Features

* **dashboard:** editorial redesign inspired by Hydrographe aesthetic ([573231a](https://github.com/MariamDouamba/water-quality-pipeline/commit/573231a699c95e8e40c936ce002c61bcd5f5cd4e)), closes [#c77b5a](https://github.com/MariamDouamba/water-quality-pipeline/issues/c77b5a) [#0c0e12](https://github.com/MariamDouamba/water-quality-pipeline/issues/0c0e12)

## [1.4.0](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.11...v1.4.0) (2026-05-12)

### Features

* **dashboard:** redesign with choropleth map, live KPIs, and fixed filters ([3b4d51f](https://github.com/MariamDouamba/water-quality-pipeline/commit/3b4d51ffd099d3d79f326cb09da210955265bc8a))

## [1.3.11](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.10...v1.3.11) (2026-05-12)

### Bug Fixes

* enhance error logging for Databricks credentials retrieval ([a711d05](https://github.com/MariamDouamba/water-quality-pipeline/commit/a711d05d4d0af6d628460b1fa0c7f049351e1315))

## [1.3.10](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.9...v1.3.10) (2026-05-12)

### Bug Fixes

* add error logging for Databricks connection failures ([e40fdc5](https://github.com/MariamDouamba/water-quality-pipeline/commit/e40fdc5345522b375f0dc45f4cafa16ecd9b3c3e))

## [1.3.9](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.8...v1.3.9) (2026-05-12)

### Bug Fixes

* update fastapi version constraint to allow newer releases ([af24def](https://github.com/MariamDouamba/water-quality-pipeline/commit/af24defbe7ccee80d2764e10cee984f0e7433ade))

## [1.3.8](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.7...v1.3.8) (2026-05-12)

### Bug Fixes

* update SQL queries for data retrieval and improve filtering conditions ([918bbeb](https://github.com/MariamDouamba/water-quality-pipeline/commit/918bbeb3d732faf866d54ebb34a27a278ac458ac))

## [1.3.7](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.6...v1.3.7) (2026-05-11)

### Bug Fixes

* force redeploy Streamlit Cloud ([20c3095](https://github.com/MariamDouamba/water-quality-pipeline/commit/20c309554a1414528ba5fa6977267b1fa119567c))

## [1.3.6](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.5...v1.3.6) (2026-05-11)

### Bug Fixes

* refactor Databricks connection to use context manager for better resource handling ([ac517d9](https://github.com/MariamDouamba/water-quality-pipeline/commit/ac517d98df278e9cd37de5e4af094c40c8a839d5))

## [1.3.5](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.4...v1.3.5) (2026-05-11)

### Bug Fixes

* suppression marker_line_color + use_container_width deprecated ([7433b51](https://github.com/MariamDouamba/water-quality-pipeline/commit/7433b513286e4ec45338baad2516b8d4c7192591))

## [1.3.4](https://github.com/MariamDouamba/water-quality-pipeline/compare/v1.3.3...v1.3.4) (2026-05-11)

### Bug Fixes

* charts Plotly + connexion Databricks via st.secrets ([a4f90da](https://github.com/MariamDouamba/water-quality-pipeline/commit/a4f90da9391a9687d5a2c7236d8ad03423d5da2d))

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
