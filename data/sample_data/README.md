# Sample data location

The application reads its canonical 1,500-row sample dataset from
`data/sample/sample_crop_data.csv` and processed data from
`data/processed/processed_data.csv`. These files are kept at their current
paths because settings, preprocessing, index generation, and model training
refer to them. The sample is locally generated synthetic test data, not an
externally sourced agricultural survey. See `docs/Dataset_Details.pdf`.
