## [0.0.15](https://github.com/justindujardin/gcspath/compare/v0.0.14...v0.0.15) (2020-04-16)


### Bug Fixes

* **requirements:** remove typer dependency ([08e8fa0](https://github.com/justindujardin/gcspath/commit/08e8fa0baa186b710a6adf2205b0a51bbd39fe37))

## [0.0.14](https://github.com/justindujardin/gcspath/compare/v0.0.13...v0.0.14) (2020-04-16)


### Bug Fixes

* **iterdir:** don't return empty results ([2a8b870](https://github.com/justindujardin/gcspath/commit/2a8b870c2ca232431c65808050363e8faff60ba2))

## [0.0.13](https://github.com/justindujardin/gcspath/compare/v0.0.12...v0.0.13) (2020-04-16)


### Bug Fixes

* **to_local:** issue where files without extensions would not be cached ([3d543a8](https://github.com/justindujardin/gcspath/commit/3d543a88a81604d13f8e401422d59803d9bb3943))

## [0.0.12](https://github.com/justindujardin/gcspath/compare/v0.0.11...v0.0.12) (2020-04-15)


### Bug Fixes

* recursion error when copying blob folders ([8b6e01c](https://github.com/justindujardin/gcspath/commit/8b6e01c3e8c35a78deee60d45563b27b7a732e9a))

## [0.0.11](https://github.com/justindujardin/gcspath/compare/v0.0.10...v0.0.11) (2020-04-15)


### Features

* **to_local:** support caching folders ([cc56f6e](https://github.com/justindujardin/gcspath/commit/cc56f6eab21f850f0521013749589ad0736e261d))

## [0.0.10](https://github.com/justindujardin/gcspath/compare/v0.0.9...v0.0.10) (2020-04-14)


### Features

* add `use_fs_caching` and `GCSPath.to_local` for caching ([2894360](https://github.com/justindujardin/gcspath/commit/2894360d48e3ac4b28ecb4627eb562f9e65b3c93))

## [0.0.9](https://github.com/justindujardin/gcspath/compare/v0.0.8...v0.0.9) (2020-04-08)


### Features

* add `resolve` method ([7cebc69](https://github.com/justindujardin/gcspath/commit/7cebc69bfc88b1a522defdce1637f5159c37def6))

## [0.0.8](https://github.com/justindujardin/gcspath/compare/v0.0.7...v0.0.8) (2020-04-08)


### Features

* allow passing GCSPath to spacy.Model.to_disk ([1d628cb](https://github.com/justindujardin/gcspath/commit/1d628cb8c5056683590d9f2403f1482e2a310971))
* **use_fs:** allow passing root folder as Path ([3635152](https://github.com/justindujardin/gcspath/commit/36351525bf84001ed4f9b0b7abf842f8e27ef1f0))

## [0.0.7](https://github.com/justindujardin/gcspath/compare/v0.0.6...v0.0.7) (2020-03-30)


### Bug Fixes

* **gcs:** gracefully handle invalid gcs client case ([529f630](https://github.com/justindujardin/gcspath/commit/529f63026abe1b11c3336febb152a030e28a85ef))

## [0.0.6](https://github.com/justindujardin/gcspath/compare/v0.0.5...v0.0.6) (2020-03-30)


### Features

* add github releases for each pypi version ([66dbed8](https://github.com/justindujardin/gcspath/commit/66dbed851346372ab84080f027113aba054452af))

## [0.0.5](https://github.com/justindujardin/gcspath/compare/v0.0.4...v0.0.5) (2020-03-30)

### Bug Fixes

- generating changelog ([ef43ed1](https://github.com/justindujardin/gcspath/commit/ef43ed11a140ed3cfaba2e7d72b7c01c7275c8d6))

## [0.0.4](https://github.com/justindujardin/gcspath/compare/v0.0.3...v0.0.4) (2020-03-30)

### Features

- support unlink path operation

## [0.0.3](https://github.com/justindujardin/gcspath/compare/v0.0.2...v0.0.3) (2020-03-30)

### Features

- **gcs:** use smart_open for streaming files ([e557ab9](https://github.com/justindujardin/gcspath/pull/3/commits/e557ab9e3bc7c0edcb02333fe8ea6be760c152dc))
- add file-system bucket adapter ([1c72f47](https://github.com/justindujardin/gcspath/pull/3/commits/1c72f475fde8de1c6cb3af23d63b793722fe82e2))
- use_fs stores buckets on the file-system ([f717280](https://github.com/justindujardin/gcspath/pull/3/commits/f7172806d0ae3e408aafc12fe7526b9852ce8b36))

## [0.0.2](v0.0.1...v0.0.2) (2020-03-18)

### Bug Fixes

- **tests:** enable unit tests on ci ([dd56011](dd56011))
