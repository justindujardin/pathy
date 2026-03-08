# CHANGELOG


## v0.14.0 (2026-03-08)

### Chores

- Codecov wants xml format
  ([`e14c46e`](https://github.com/justindujardin/pathy/commit/e14c46e714f8c7cecf555940d01d2b847a0d433e))

- Missing coverage and fixed pypi badge
  ([`65ddbd1`](https://github.com/justindujardin/pathy/commit/65ddbd162790dd89c6e98b6641c772f7d60dba80))

- Noone but me would ever know it was 99.91%, but I would
  ([`6a572fc`](https://github.com/justindujardin/pathy/commit/6a572fce3b0a0daa26ebc05ddcc51350142d52c1))

- patch cover the os nt check

- Replace semantic-release (node) with (python)
  ([#129](https://github.com/justindujardin/pathy/pull/129),
  [`3b4cf5d`](https://github.com/justindujardin/pathy/commit/3b4cf5d9993ace372b23c16d9041321324295a35))

* chore: replace semantic-release (node) with (python)

* chore: fix codecov reporting

### Documentation

- Cleanup
  ([`eca70a4`](https://github.com/justindujardin/pathy/commit/eca70a4cec6a21df3a05cefba0c66abde59caeeb))

### Features

- **cli**: Make typer an optional dependency that's installed with pathy[cli]
  ([#130](https://github.com/justindujardin/pathy/pull/130),
  [`f9c2fbd`](https://github.com/justindujardin/pathy/commit/f9c2fbd2edef1f81f0cecf952b5e284a9763507d))

- closes #99

BREAKING CHANGE: The `pathy` CLI app is only available when installing all extras, or the
  `pathy[cli]` extra specifically. A helpful error is shown to aid in resolving any issues that
  arise from this change.

### Breaking Changes

- **cli**: The `pathy` CLI app is only available when installing all extras, or the `pathy[cli]`
  extra specifically. A helpful error is shown to aid in resolving any issues that arise from this
  change.


## v0.13.0 (2026-03-08)

### Chores

- Fix codecov config
  ([`5447f8d`](https://github.com/justindujardin/pathy/commit/5447f8d1be5282bfbfb80512152980a39306034e))

- Update codecov link in readme
  ([`6aecc6a`](https://github.com/justindujardin/pathy/commit/6aecc6a011f36867bb5d1d4a075e84ecd35c8580))

### Features

- Upgrade to pathlib_abc 0.3.x API ([#123](https://github.com/justindujardin/pathy/pull/123),
  [`eb7d445`](https://github.com/justindujardin/pathy/commit/eb7d445d1015b1e56ddf049c859e6ba6fa495b83))

- Migrate PurePathy/Pathy to pathlib_abc 0.3.x - replace pathmod with parser - implement
  drive/root/anchor properties - add split/splitdrive/splitext to pathmod - update method signatures
  (follow_symlinks, recurse_symlinks) - remove _make_child_entry - drop old requirement files

BREAKING CHANGE: PurePathy.match() no longer auto-prepends '**' to patterns. Use full_match() for
  recursive matching, or explicitly add '**/' to patterns.

- Upgrade to pathlib_abc 0.5.x API ([#128](https://github.com/justindujardin/pathy/pull/128),
  [`71fe8e5`](https://github.com/justindujardin/pathy/commit/71fe8e5c8e5401e54c5c4aa95dab044a442bc2a5))

- PurePathBase -> JoinablePath - PathBase -> ReadablePath + WritablePath - implement
  __vfspath__/info/__open_reader__/__open_writer__ - add altsep to pathmod parser protocol

BREAKING CHANGE: PurePathy no longer implements __fspath__. Cloud paths are not local filesystem
  paths, so os.fspath() no longer works on them. Use str(path) instead.

### Breaking Changes

- Purepathy no longer implements __fspath__. Cloud paths are not local filesystem paths, so
  os.fspath() no longer works on them. Use str(path) instead.


## v0.12.0 (2026-03-07)

### Chores

- Drop old tool scripts
  ([`2770c0f`](https://github.com/justindujardin/pathy/commit/2770c0fd7a8c5f123f5d7173e8668ecd2b57d4ad))

- Fix lint issues
  ([`e95d7c5`](https://github.com/justindujardin/pathy/commit/e95d7c5866ff2c673c859a2d019dd53334c161a9))

- Fix running tests on pr branches?
  ([`d96a590`](https://github.com/justindujardin/pathy/commit/d96a590b8ce1bb39e495e29239b74eb2269e75aa))

- maybe the master target changed in meaning? or maybe it was ignored before? idk, but this mirrors
  the setup from my other working projects :shrug:

- Install uv on deploy task
  ([`59316e7`](https://github.com/justindujardin/pathy/commit/59316e716c597d91dde10117003ecb0f875db81e))

- Update readme docs
  ([`61c7704`](https://github.com/justindujardin/pathy/commit/61c7704c6a0eaf423bf4536a573a5e6c6743e05e))

- TODO: why isn't this part of the automation? :sob:

### Documentation

- **readme**: Cleanup docs [skip ci]
  ([`5f5d521`](https://github.com/justindujardin/pathy/commit/5f5d521d8c4d37793eb3283d778ba4524e715b51))

- **readme**: Cleanup docs [skip ci]
  ([`83610d3`](https://github.com/justindujardin/pathy/commit/83610d321b8858ef736d1eef95f16c39fa5d88cb))

- **readme**: Cleanup install quick start
  ([`a6d364c`](https://github.com/justindujardin/pathy/commit/a6d364c79db45e1116404f283b2db3c8cd80fe62))

### Features

- Modernize build system, add Python 3.12/3.13 support
  ([`1b45c22`](https://github.com/justindujardin/pathy/commit/1b45c220a1a94d2da1e3e47012bba6dbfa0d0644))

- Migrate from setup.py to pyproject.toml + hatchling - Switch from virtualenv/pip to uv for
  dependency management - Add Python 3.12 and 3.13 to test matrix - Drop Python 3.8 and 3.9 (EOL) -
  Loosen typer version constraint (remove <1.0.0 cap) - Clean up CI workflows and dead tool scripts
  - Remove auto-doc pipeline (mathy_pydoc incompatible with Python 3.13)

BREAKING CHANGE: Python 3.8 and 3.9 are no longer supported. Minimum required version is now Python
  3.10.

- **pypi**: Relax smart_open range to include 7.x.x
  ([#117](https://github.com/justindujardin/pathy/pull/117),
  [`7ee604e`](https://github.com/justindujardin/pathy/commit/7ee604ed2b7c2495c50471dc28e3298f0c636153))

* feat(pypi): relax smart_open range to include 7.x.x

* chore: update build script for latest action versions

### Breaking Changes

- Python 3.8 and 3.9 are no longer supported. Minimum required version is now Python 3.10.


## v0.11.0 (2024-01-11)

### Features

- Drop Python 3.7 and add Python 3.12 ([#112](https://github.com/justindujardin/pathy/pull/112),
  [`97ebaa1`](https://github.com/justindujardin/pathy/commit/97ebaa11ec62ce551b96a3c2431f8a29777ed30d))

* fix(pypi): drop end-of-life python 3.7 support

BREAKING CHANGE: This drops support for python 3.7 which has reached its end of life

* feat(Pathy): integrate pathlib_abc - replace base pathlib.Path class with abstract base class from
  a future version of python.

BREAKING CHANGE: Pathy.key returns a str rather than a Pathy instance

* feat(ci): add python 3.12

BREAKING CHANGE: Pathy no longer inherits from pahtlib.Path

This means Pathy does not support directly accepting and working with file system paths. You must
  use Pathy.fluid or pathlib.Path to construct your file system paths. Pathy will continue to
  interoperate with them as needed to accommodate its public API.

### Breaking Changes

- This drops support for python 3.7 which has reached its end of life

- Pathy.key returns a str rather than a Pathy instance

- Pathy no longer inherits from pahtlib.Path


## v0.10.3 (2023-10-22)

### Bug Fixes

- **is_dir**: Return False if bucket does not exist (#107 by @yaelmi3)
  ([`4a4e69d`](https://github.com/justindujardin/pathy/commit/4a4e69dcb45a79d4183613362fa8bb94b14290dc))

* fix(is_dir): return False if bucket does not exist

- I believe this might stem from there actually being a bucket that exists with the name provided
  "not-a-real-bucket" - try generating a really unique bucket name rather than adding any
  assumptions about Forbidden meaning doesn't exist unless we have to


## v0.10.2 (2023-06-19)

### Bug Fixes

- **python**: Add follow_symlinks for py 3.11.4
  ([#104](https://github.com/justindujardin/pathy/pull/104),
  [`49a53b5`](https://github.com/justindujardin/pathy/commit/49a53b58d0edd07de071df53b6b041994866e8c8))

### Chores

- **ci**: Fix node version so github stops complaining
  ([#103](https://github.com/justindujardin/pathy/pull/103),
  [`78a3730`](https://github.com/justindujardin/pathy/commit/78a3730098f89e8e8478976229e3474114eebccb))

- **deploy**: Fix script by removing string escapes
  ([`2350cd2`](https://github.com/justindujardin/pathy/commit/2350cd2dca271cebeb94a484b3ab362c9e4a6fc0))

On windows this is needed for the command to work. On linux it's an error. 😅

- **deps**: Bump yaml, semantic-release, husky and lint-staged
  ([#101](https://github.com/justindujardin/pathy/pull/101),
  [`09a83f0`](https://github.com/justindujardin/pathy/commit/09a83f040bd9df653974b6f208ec3de00e6a1454))

* chore(deps): bump yaml, semantic-release, husky and lint-staged

Bumps [yaml](https://github.com/eemeli/yaml) to 2.2.2 and updates ancestor dependencies
  [yaml](https://github.com/eemeli/yaml),
  [semantic-release](https://github.com/semantic-release/semantic-release),
  [husky](https://github.com/typicode/husky) and
  [lint-staged](https://github.com/okonet/lint-staged). These dependencies need to be updated
  together.

Updates `yaml` from 1.10.2 to 2.2.2 - [Release notes](https://github.com/eemeli/yaml/releases) -
  [Commits](https://github.com/eemeli/yaml/compare/v1.10.2...v2.2.2)

Updates `semantic-release` from 19.0.3 to 21.0.1 - [Release
  notes](https://github.com/semantic-release/semantic-release/releases) -
  [Commits](https://github.com/semantic-release/semantic-release/compare/v19.0.3...v21.0.1)

Updates `husky` from 4.3.8 to 8.0.3 - [Release notes](https://github.com/typicode/husky/releases) -
  [Commits](https://github.com/typicode/husky/compare/v4.3.8...v8.0.3)

Updates `lint-staged` from 10.5.4 to 13.2.1 - [Release
  notes](https://github.com/okonet/lint-staged/releases) -
  [Commits](https://github.com/okonet/lint-staged/compare/v10.5.4...v13.2.1)

--- updated-dependencies: - dependency-name: yaml dependency-type: indirect

- dependency-name: semantic-release dependency-type: direct:development

- dependency-name: husky dependency-type: direct:development

- dependency-name: lint-staged dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

* chore: update black for CI build

* feat(python): drop pytho 3.6 support

3.6 is end of life

* chore: update dev status and drop py3.6

---------

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: Justin DuJardin <justindujardin@users.noreply.github.com>


## v0.10.1 (2022-12-08)

### Bug Fixes

- **smart_open**: Relax range to < 7.0 ([#98](https://github.com/justindujardin/pathy/pull/98),
  [`43d1327`](https://github.com/justindujardin/pathy/commit/43d13272286e2d34a56c23a27ca4e97d037e8888))


## v0.10.0 (2022-11-23)

### Bug Fixes

- **stat**: Return BlobStat for all pathy paths
  ([#96](https://github.com/justindujardin/pathy/pull/96),
  [`f092605`](https://github.com/justindujardin/pathy/commit/f092605c015e57e66ce88b98502da917c08ed4f3))

* fix(stat): return BlobStat for all pathy paths

- implement `stat` in `BasePath` and yield `BlobStat`s instead of `os.stat_result`. - implement all
  the pathlib file mode checking helpers because they use `self.stat()` internally which doesn't
  work with BlobStats. - add tests for base path helpers - update CLI test to assert that stats are
  BlobStat now

BREAKING CHANGE: Previously when using Pathy.fluid paths that point to local file system paths,
  Pathy would return an `os.stat_result` rather than a `BlobStat`. This made it difficulty to treat
  mixed paths consistently.

Now Pathy returns a BlobStat structure for local and remote paths.

If you need to use `os.stat_result` you can still call `os.stat(my_path)` to access it.

### Breaking Changes

- **stat**: Previously when using Pathy.fluid paths that point to local file system paths, Pathy
  would return an `os.stat_result` rather than a `BlobStat`. This made it difficulty to treat mixed
  paths consistently.


## v0.9.0 (2022-11-22)

### Bug Fixes

- **blob**: Properly initialize default last_modified
  ([`d831bee`](https://github.com/justindujardin/pathy/commit/d831bee6d82a02bf048f64384864a1c8a590ef1b))

- change the default of last_modified to None instead of -1. This is because last_modified is
  defined as an optional int, so None is the proper default.

- **windows**: Consistent path separator in resolve
  ([`44f5ca0`](https://github.com/justindujardin/pathy/commit/44f5ca0cf5984fd8a0d6071060e65064ec2b163c))

- the unerlying abspath() call on windows resolves with \\ slashes, which we don't want when
  referring to bucket paths. BasePath (pathlib.Path) variants don't do this translation to preserve
  the os-specific slashes.

- **windows**: File:/// paths had the wrong suffix
  ([`674a109`](https://github.com/justindujardin/pathy/commit/674a10926505bdfcbc5ad0482309dfa02974c9fa))

- on Windows Pathy normally only deals with bucket formats using / slashes, but when using the
  file:/// scheme you would have a Pathy object that contains \\ separators to represent a windows
  file path. In this case, convert the separator to \\ while formatting strings.

- **windows**: Return None owner on windows where not implemented
  ([`abd28c4`](https://github.com/justindujardin/pathy/commit/abd28c46ac6f7708a3591722ad862cb73d3af318))

- windows doesn't implement owner() in pathlib, so catch the error and return None like other
  corner-cases

### Chores

- Cleanup from review
  ([`35d8525`](https://github.com/justindujardin/pathy/commit/35d8525d035f1e653680091c030460c85b502480))

- Fix lint
  ([`487dad4`](https://github.com/justindujardin/pathy/commit/487dad404a0539cf87986583ec31dc4efc14b3ef))

- Remove /Q from test package workflow
  ([`39950f6`](https://github.com/justindujardin/pathy/commit/39950f66bd9c0b1fd9a72e9fa829fee45608e042))

- Remove sh from windows build scripts
  ([`61b0058`](https://github.com/justindujardin/pathy/commit/61b005865bf4ef52396d03cb386000e60dbfc949))

- Use rm github action instead of rmdir
  ([`4f1582f`](https://github.com/justindujardin/pathy/commit/4f1582fbeba1d37913c7035743a2079ba42f1379))

- the github runner doesn't like the rmdir arguments :shrug:

- **windows**: Add a few path test cases
  ([`390baa1`](https://github.com/justindujardin/pathy/commit/390baa13a1600320f81a0c9436bf4c7b51a1c86c))

- **windows**: Update make_uri test for win paths
  ([`bae873f`](https://github.com/justindujardin/pathy/commit/bae873f50f979c52ba9e0376573bac78fd485c33))

### Features

- **Pathy**: Raise error when not using Pathy.fluid for absolute paths
  ([`e7f4e73`](https://github.com/justindujardin/pathy/commit/e7f4e73b0b1bed8a68588e81f8bc3c5c74ed71ad))

- this addresses concerns around initializing Pathy paths with unix and windows absolute paths. The
  correct way to initialize these paths is to use Pathy.fluid. - raise an error if an absolute
  system path is given when initializing Pathy objects - fixes #87

BREAKING CHANGE: Previously Pathy would allow you to initialize Pathy instances with absolute system
  paths (unix and windows). Now Pathy raises a ValueError if given an absolute system path that
  suggest using Pathy.fluid instead.

- **windows**: Add windows CI test execution
  ([`504823d`](https://github.com/justindujardin/pathy/commit/504823dde36c1ab3fb778d31a7d25339a133a6d8))

- verify some path shenanigans with Windows are working as expected

### Testing

- **cli**: Ls -l different year formatting test
  ([`1a0abc8`](https://github.com/justindujardin/pathy/commit/1a0abc820452ee74e76a5c574ab7c97a0fe533e4))

- **windows**: Add windows specific path tests
  ([`73ddfa1`](https://github.com/justindujardin/pathy/commit/73ddfa1fcfea36e9fb3d56dc512b75cd00d7e159))


## v0.8.1 (2022-11-16)

### Bug Fixes

- **azure**: "azure" scheme was not registered
  ([#94](https://github.com/justindujardin/pathy/pull/94),
  [`2791565`](https://github.com/justindujardin/pathy/commit/279156530e8b88e5fbc27c58da034b441511dc6c))


## v0.8.0 (2022-11-16)

### Features

- **azure**: Support azure blob container storage
  ([#93](https://github.com/justindujardin/pathy/pull/93),
  [`9624856`](https://github.com/justindujardin/pathy/commit/962485661a67a87f7b0cdccb25ee135a0faa7614))

* feat(azure): support azure blob container storage

- add azure implementation, and register with scheme "azure" - update test suite to use azure client
  when "azure" adapter is requested - add `pathy[azure]` extras to setup.py - remove "list_buckets"
  from BucketClient classes

BREAKING CHANGE: This removes an internal bit of code that allows for enumerating buckets in certain
  situations. The API was impossible to reach without going indirectly through the glob
  functionality, and it's unclear whether the code paths were ever reached outside of specific unit
  testing situations. If there's an explicit need for listing buckets, we can add a top-level API
  for it.

### Breaking Changes

- **azure**: This removes an internal bit of code that allows for enumerating buckets in certain
  situations. The API was impossible to reach without going indirectly through the glob
  functionality, and it's unclear whether the code paths were ever reached outside of specific unit
  testing situations. If there's an explicit need for listing buckets, we can add a top-level API
  for it.


## v0.7.1 (2022-11-15)

### Bug Fixes

- **pypi**: Add classifiers for python 3.10 / 3.11
  ([`515cb5d`](https://github.com/justindujardin/pathy/commit/515cb5d69c7be9a324b8c144d97671803d33401e))

I missed this bit while adding support for python 3.11 in #89

* chore: keep codecov from reporting early

Builds look failed until all the tasks are done. Codecov's site says that `require_ci_to_pass` is
  default yes. 🤷

Add after_n_builds set to the number of build tasks we have.


## v0.7.0 (2022-11-15)

### Features

- **python**: Support python 3.11
  ([`c2a0586`](https://github.com/justindujardin/pathy/commit/c2a0586c198a19cf6fcf81b41c60689af574db17))

- drop the use of _Accessor class from the internals of pathlib. It was removed in python 3.11 which
  broke... everything. - Detect python < 3.11 and provide the base needed accessor method "scandir"
  - Detect python >= 3.11 and provide the Path._scandir function - Move accessor methods to the
  Pathy class - Remove a few _accessor tests, and update those that referenced the accessor directly
  - TODO: Remove the use of pathlib scandir entirely, and replace it with an inlined glob matching
  system to provide this functionality. This is the only tech debt the project has left at this
  point that I can see.

BREAKING CHANGE: Pathy.exists() no longer enumerates buckets if given a path with no root.

### Breaking Changes

- **python**: Pathy.exists() no longer enumerates buckets if given a path with no root.


## v0.6.2 (2022-06-30)

### Bug Fixes

- **smart_open**: Use compression flag required by 6.x versions
  ([`8c5f092`](https://github.com/justindujardin/pathy/commit/8c5f09221702261e0f35f60fd2663e4ab42d2cf9))

Also this fix works `pathy` with `smart-open` 6.0.0

Co-authored-by: Alexander Shadchin <shadchin@yandex-team.com>

### Chores

- Fix build hangs during setup ([#75](https://github.com/justindujardin/pathy/pull/75),
  [`d8e03af`](https://github.com/justindujardin/pathy/commit/d8e03af94b46547da55f1dcd46efeeb531ac8819))

- the dev dependencies were too unspecified, so the pip resolver was taking forever to install
  packages

- Pin mypy and pyright versions ([#84](https://github.com/justindujardin/pathy/pull/84),
  [`2fbd16f`](https://github.com/justindujardin/pathy/commit/2fbd16f2bd1b51997769e505e98716c62facd9e6))

* chore: pin mypy and pyright versions

- it's a bummer getting small PRs with busted builds. We can update the versions manually if needed.

* chore: make sure to use local pyright version

- Restore old typer range ([#80](https://github.com/justindujardin/pathy/pull/80),
  [`ef84745`](https://github.com/justindujardin/pathy/commit/ef84745cd4553b11ede4aebda69fe28745c60add))

- Update node build version to 16 ([#85](https://github.com/justindujardin/pathy/pull/85),
  [`76638e0`](https://github.com/justindujardin/pathy/commit/76638e0a73a17441e14320d299a111aa2adec71f))

- latest semantic release requires it

- Update npm deps from audit ([#79](https://github.com/justindujardin/pathy/pull/79),
  [`21a2d0f`](https://github.com/justindujardin/pathy/commit/21a2d0f717131313199dec77f2168a554a0b4434))

- **deps**: Bump node-fetch from 2.6.1 to 2.6.7
  ([#74](https://github.com/justindujardin/pathy/pull/74),
  [`a3f92e6`](https://github.com/justindujardin/pathy/commit/a3f92e6af76d42f7490e5cc26363e4bc60ae9ec8))

Bumps [node-fetch](https://github.com/node-fetch/node-fetch) from 2.6.1 to 2.6.7. - [Release
  notes](https://github.com/node-fetch/node-fetch/releases) -
  [Commits](https://github.com/node-fetch/node-fetch/compare/v2.6.1...v2.6.7)

--- updated-dependencies: - dependency-name: node-fetch dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump tar from 4.4.13 to 4.4.19 ([#72](https://github.com/justindujardin/pathy/pull/72),
  [`869e62b`](https://github.com/justindujardin/pathy/commit/869e62b2fe2c68708cc6e2a719cb073f29f0f8c3))

Bumps [tar](https://github.com/npm/node-tar) from 4.4.13 to 4.4.19. - [Release
  notes](https://github.com/npm/node-tar/releases) -
  [Changelog](https://github.com/npm/node-tar/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/npm/node-tar/compare/v4.4.13...v4.4.19)

--- updated-dependencies: - dependency-name: tar dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump trim-off-newlines from 1.0.1 to 1.0.3
  ([#73](https://github.com/justindujardin/pathy/pull/73),
  [`582643a`](https://github.com/justindujardin/pathy/commit/582643a48aba06c053bc27d777691cb3d00c3b5b))

Bumps [trim-off-newlines](https://github.com/stevemao/trim-off-newlines) from 1.0.1 to 1.0.3. -
  [Release notes](https://github.com/stevemao/trim-off-newlines/releases) -
  [Commits](https://github.com/stevemao/trim-off-newlines/compare/v1.0.1...v1.0.3)

--- updated-dependencies: - dependency-name: trim-off-newlines dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump minimist from 1.2.5 to 1.2.6
  ([#70](https://github.com/justindujardin/pathy/pull/70),
  [`be99d85`](https://github.com/justindujardin/pathy/commit/be99d85363c61c224effaa73840acc52d1fa2662))

Bumps [minimist](https://github.com/substack/minimist) from 1.2.5 to 1.2.6. - [Release
  notes](https://github.com/substack/minimist/releases) -
  [Commits](https://github.com/substack/minimist/compare/1.2.5...1.2.6)

--- updated-dependencies: - dependency-name: minimist dependency-type: direct:development ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps-dev**: Bump semantic-release from 17.3.8 to 19.0.3
  ([#82](https://github.com/justindujardin/pathy/pull/82),
  [`8478757`](https://github.com/justindujardin/pathy/commit/847875765fe05bf9378b15bc00bdf2376329fcee))

* chore(deps-dev): bump semantic-release from 17.3.8 to 19.0.3

Bumps [semantic-release](https://github.com/semantic-release/semantic-release) from 17.3.8 to
  19.0.3. - [Release notes](https://github.com/semantic-release/semantic-release/releases) -
  [Commits](https://github.com/semantic-release/semantic-release/compare/v17.3.8...v19.0.3)

--- updated-dependencies: - dependency-name: semantic-release dependency-type: direct:development
  ...

Signed-off-by: dependabot[bot] <support@github.com>

* chore: bump peer dependencies of semantic-release

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

Co-authored-by: Justin DuJardin <justin@dujardinconsulting.com>


## v0.6.1 (2021-10-25)

### Bug Fixes

- Update for Python 3.10 compatibility ([#68](https://github.com/justindujardin/pathy/pull/68),
  [`450c2f2`](https://github.com/justindujardin/pathy/commit/450c2f206efefe3d96e24294f5d02f8e9ceaf4ff))

### Chores

- **deps**: Bump path-parse from 1.0.6 to 1.0.7
  ([#64](https://github.com/justindujardin/pathy/pull/64),
  [`43eb4e0`](https://github.com/justindujardin/pathy/commit/43eb4e08a55fc488ea4566399b31ea3d161e0b0d))

Bumps [path-parse](https://github.com/jbgutierrez/path-parse) from 1.0.6 to 1.0.7. - [Release
  notes](https://github.com/jbgutierrez/path-parse/releases) -
  [Commits](https://github.com/jbgutierrez/path-parse/commits/v1.0.7)

--- updated-dependencies: - dependency-name: path-parse dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>


## v0.6.0 (2021-06-26)

### Chores

- Fix error in deploy script
  ([`c774efa`](https://github.com/justindujardin/pathy/commit/c774efa6feb7fdfcdbd4fd37a4048a403cdf5c38))

- ignore twine "already exists" errors because we always try to upload. :sweat:

- **ci**: Add mock/dataclass type stubs ([#62](https://github.com/justindujardin/pathy/pull/62),
  [`156480e`](https://github.com/justindujardin/pathy/commit/156480e424f2a8c316683344461ed013355a5a87))

- **deps**: Bump glob-parent from 5.1.1 to 5.1.2
  ([#60](https://github.com/justindujardin/pathy/pull/60),
  [`ffa1a13`](https://github.com/justindujardin/pathy/commit/ffa1a136ce3f0413a2b725c9471fac9e59abdb87))

Bumps [glob-parent](https://github.com/gulpjs/glob-parent) from 5.1.1 to 5.1.2. - [Release
  notes](https://github.com/gulpjs/glob-parent/releases) -
  [Changelog](https://github.com/gulpjs/glob-parent/blob/main/CHANGELOG.md) -
  [Commits](https://github.com/gulpjs/glob-parent/compare/v5.1.1...v5.1.2)

--- updated-dependencies: - dependency-name: glob-parent dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump handlebars from 4.7.6 to 4.7.7
  ([#56](https://github.com/justindujardin/pathy/pull/56),
  [`5300ebd`](https://github.com/justindujardin/pathy/commit/5300ebdad8b9a45abd51da1d32b289b862b3bded))

Bumps [handlebars](https://github.com/wycats/handlebars.js) from 4.7.6 to 4.7.7. - [Release
  notes](https://github.com/wycats/handlebars.js/releases) -
  [Changelog](https://github.com/handlebars-lang/handlebars.js/blob/master/release-notes.md) -
  [Commits](https://github.com/wycats/handlebars.js/compare/v4.7.6...v4.7.7)

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump lodash from 4.17.19 to 4.17.21
  ([#57](https://github.com/justindujardin/pathy/pull/57),
  [`048aa71`](https://github.com/justindujardin/pathy/commit/048aa7137086267c8849b054f0a6b1f9c058f917))

Bumps [lodash](https://github.com/lodash/lodash) from 4.17.19 to 4.17.21. - [Release
  notes](https://github.com/lodash/lodash/releases) -
  [Commits](https://github.com/lodash/lodash/compare/4.17.19...4.17.21)

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump normalize-url from 5.3.0 to 5.3.1
  ([#58](https://github.com/justindujardin/pathy/pull/58),
  [`ed7b095`](https://github.com/justindujardin/pathy/commit/ed7b095a4efd4eb66ef736a73db027c807faf18f))

Bumps [normalize-url](https://github.com/sindresorhus/normalize-url) from 5.3.0 to 5.3.1. - [Release
  notes](https://github.com/sindresorhus/normalize-url/releases) -
  [Commits](https://github.com/sindresorhus/normalize-url/commits)

--- updated-dependencies: - dependency-name: normalize-url dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

- **deps**: Bump trim-newlines from 3.0.0 to 3.0.1
  ([#59](https://github.com/justindujardin/pathy/pull/59),
  [`ecedf06`](https://github.com/justindujardin/pathy/commit/ecedf06b140ad5fdbbc1bd96b902be2a674d4ee3))

Bumps [trim-newlines](https://github.com/sindresorhus/trim-newlines) from 3.0.0 to 3.0.1. - [Release
  notes](https://github.com/sindresorhus/trim-newlines/releases) -
  [Commits](https://github.com/sindresorhus/trim-newlines/commits)

--- updated-dependencies: - dependency-name: trim-newlines dependency-type: indirect ...

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- Support smart_open >=5.0.0,<6.0.0 ([#63](https://github.com/justindujardin/pathy/pull/63),
  [`9718752`](https://github.com/justindujardin/pathy/commit/97187528b70fdb96e928e1f90a3b06732e126b16))

* feat: increase smart_open version range to < 6.0.0 * chore: update s3 session for smart_open >= 5

BREAKING CHANGE: This change removes support for smart_open < 5.0.0

The API for specifying s3 credentials changed in smart_open v5, so previous versions are
  incompatible.

### Breaking Changes

- This change removes support for smart_open < 5.0.0


## v0.5.2 (2021-04-24)

### Features

- **cli**: Add version number to cli help string
  ([#55](https://github.com/justindujardin/pathy/pull/55),
  [`8001907`](https://github.com/justindujardin/pathy/commit/800190760759f35a545948a12417952451e7891f))


## v0.5.1 (2021-04-23)

### Features

- **clients**: Add support for S3 bucket storage
  ([#54](https://github.com/justindujardin/pathy/pull/54),
  [`5bb7e1b`](https://github.com/justindujardin/pathy/commit/5bb7e1b8faa422c8a80d91d7d8e71f6de4052962))

* feat(clients): support for "s3://bucket/blobs"

- install with `pip install pathy[s3]` extras - update tests to substitute the scheme where needed
  instead of hardcoded "gs"

* chore: cleanup from review

* test(s3): exercise list_buckets and pagination codepaths

* chore: fix passing credentials through the env

* chore: fix leftover dev change in conftest

* chore: tighten up missing extras tests

- specifically disable use_fs incase it was still set from another test

* chore: fix passing s3 creds to smart_open

- add env vars for s3

* chore(readme): add cloud platform support table


## v0.5.0 (2021-04-22)

### Bug Fixes

- **auto-import**: Move public exports into __init__.py
  ([`fd09021`](https://github.com/justindujardin/pathy/commit/fd090215efc392e76d167e9c0203520c251578da))

- it seems that pylance can't manage to auto-import symbols with short paths unless they're defined
  in __init__.py. - it's supposed to be the case that it just magically picks the shortest import
  path, but it doesn't work in my testing.

BREAKING CHANGE: Previously you could import symbols directly from their files in the module, e.g.
  `from pathy.base import Pathy`. Now you must import them from the base package, e.g. `from pathy
  import Pathy`.

- **cli**: Ls returns code 1 from invalid sources
  ([`b2ff829`](https://github.com/justindujardin/pathy/commit/b2ff829f35db6b5af25c9bc553f1e1b76be7e39c))

- this is more consistent with unix ls command, and was the intention before. - add tests for return
  code

BREAKING CHANGES: the `pathy ls` command used to return code 0 if you gave it an invalid path. Now
  it returns exit code 1 similar to the unix `ls` command.

- **samefile**: Compare self.key to other.key not self.key
  ([`688628e`](https://github.com/justindujardin/pathy/commit/688628ecbf430284fbcb83142d7751e0b54475d2))

- heh, heh :/

### Chores

- Add back travis script
  ([`3982d1b`](https://github.com/justindujardin/pathy/commit/3982d1b9b13ee8070521ff2551590fdd0a8b44db))

- Add breaking changes note
  ([`3e53f21`](https://github.com/justindujardin/pathy/commit/3e53f217d83b183effe452d70d3a394481f72bdc))

- Add build step
  ([`f0fdcfa`](https://github.com/justindujardin/pathy/commit/f0fdcfa768b73de18d739ad5ca62019ea18fb042))

- Add checkout to deploy job
  ([`ecbc5fa`](https://github.com/justindujardin/pathy/commit/ecbc5fa6e25d99d610403cc8e551a95a8a9bead5))

- no wonder it can't find the deploy script :sweat_smile: - remove mac testing for now. It's cool to
  be able to do, but there's no platform specific code, and it takes longer to execute (sometimes up
  to 6 minutes) - add back python 3.7 and 3.8

- Add deploy step to github action
  ([`a102df4`](https://github.com/justindujardin/pathy/commit/a102df424f71132138d395eae4e8e864c877ea4f))

- only runs on master. testing these kinds of changes is always "fun" :sweat_smile:

- Add ENV_ID to cli tests
  ([`c6ecf6a`](https://github.com/justindujardin/pathy/commit/c6ecf6a3efb28940f621081e8aa9285d0498580a))

- Add platform to unique env id
  ([`f3f59db`](https://github.com/justindujardin/pathy/commit/f3f59dbcb69676b925a068a0b16879d1cf907ba7))

- when running matrix tests we need unique locations to write to in each bucket so the tests don't
  conflict with each other. Adding the platform means we can run MacOS python 3.6 tests at the same
  time as Ubuntu python 3.6 tests.

- Add py 3.9 to setup.py classifiers
  ([`0f7b73b`](https://github.com/justindujardin/pathy/commit/0f7b73bc27b44c11b31c4fa4ecee2c97429f2383))

- Add skip for gcs tests if extra is not installed
  ([`431e631`](https://github.com/justindujardin/pathy/commit/431e631ef0765851c2c47204c39724b6c9ff3583))

- Break up the huge test_base.py file
  ([`7a40603`](https://github.com/justindujardin/pathy/commit/7a406032ffd3edf8ff82103f14200bf33d15ebb7))

- add a few more corner cases to client testing

- Call virtualenv with python
  ([`5cbe076`](https://github.com/justindujardin/pathy/commit/5cbe07642f58356cceeff0f248a6c16e09366f74))

- Cleanup
  ([`cb1983b`](https://github.com/justindujardin/pathy/commit/cb1983bf1684f64960793d84759416b9b8b7d7a4))

- Cleanup action steps
  ([`b5a5618`](https://github.com/justindujardin/pathy/commit/b5a561889702620f24cc698c9a175aacf83af687))

- add codecov token for reporting coverage

- Cleanup from review
  ([`e61fb01`](https://github.com/justindujardin/pathy/commit/e61fb01f19e44c78dca457e11c45ed44307a00da))

- Cleanup from review
  ([`2ba9400`](https://github.com/justindujardin/pathy/commit/2ba94001c4cc2fd7f42d1e95f24e5b5ba443689f))

- Cleanup from review
  ([`351ecd0`](https://github.com/justindujardin/pathy/commit/351ecd019b75b9b5744813a4b4a0cdd794c45653))

- Cleanup from review
  ([`a664b75`](https://github.com/justindujardin/pathy/commit/a664b753ed36c19d235eed7a4fbf5fc2285a8edb))

- Cleanup from review
  ([`d244649`](https://github.com/justindujardin/pathy/commit/d24464971d00e52fa8e7bf0793dba7bbc31671e1))

- Cleanup lint
  ([`a5a5a2b`](https://github.com/justindujardin/pathy/commit/a5a5a2b84b0bd6fa7921c8601c868b11b46bd091))

- Cleanup ordering assumptions in tests
  ([`9f6f44b`](https://github.com/justindujardin/pathy/commit/9f6f44b509049650abeb0478527b0f104eb7405f))

- Delay GCS imports in tests to allow running without extras
  ([`27aad4f`](https://github.com/justindujardin/pathy/commit/27aad4fc715c04442c6fe868051285186082e054))

- Drop travis build script
  ([`a14a3f4`](https://github.com/justindujardin/pathy/commit/a14a3f41722f13b4d374a072163efa0d7aab7338))

- Drop travis script
  ([`4c4bc46`](https://github.com/justindujardin/pathy/commit/4c4bc46dc594c702e1350731426c36257a0cdaf6))

- Enable other python versions
  ([`040763e`](https://github.com/justindujardin/pathy/commit/040763e5489dfba11672bc45054dffa387ca9f1e))

- Fix fixtures path in manifest
  ([`99c0130`](https://github.com/justindujardin/pathy/commit/99c0130e7974e3f5f7b9eb709a07edc67620fdef))

- Fix lint
  ([`824650c`](https://github.com/justindujardin/pathy/commit/824650cff782c4813d63580ba4458f9407ed1798))

- Fix lint
  ([`41abaf9`](https://github.com/justindujardin/pathy/commit/41abaf9db872eb13248e851af2d6ad0dcbc35772))

- Fix lint in cli
  ([`23840d6`](https://github.com/justindujardin/pathy/commit/23840d6665b912b95c89880ffaea462438ce1ce9))

- Fix test skip if spacy is missing
  ([`e3c9b75`](https://github.com/justindujardin/pathy/commit/e3c9b75fe9200544c649c4608ffe42d8cf0134b8))

- Ignore __main__ invocation in coverage
  ([`36f7517`](https://github.com/justindujardin/pathy/commit/36f75178287a9aa4b33808f0da8525dbed37fb43))

- Install virtualenv first
  ([`7e0ff2a`](https://github.com/justindujardin/pathy/commit/7e0ff2a237bd561391eee8b485fa4911d2797838))

- Misc DRY cleanup in tests
  ([`e094dfc`](https://github.com/justindujardin/pathy/commit/e094dfc6e9df53de41801b123807f6ccf13bed86))

- Remove extra _gcs and _types files
  ([`7fddd11`](https://github.com/justindujardin/pathy/commit/7fddd11b55d04c4782a2dcd4bfe90edbd3af2265))

- Remove source folder when testing wheels in CI
  ([`a385758`](https://github.com/justindujardin/pathy/commit/a385758ad9c7ca6ab0e64ff7c4f2cee5235e091e))

- Run set-build-version with nodejs
  ([`c374e75`](https://github.com/justindujardin/pathy/commit/c374e75c7c48fabdbf2b9a0c7414e60e8f0c6731))

- Simplify _init body for better coverage
  ([`a88922a`](https://github.com/justindujardin/pathy/commit/a88922a4956057a5b248379cd9d1e8c5c84bef15))

- in practice we don't pass a template to the _init() function, because it's only ever used in
  helper functions like Path.resolve/absolute that Pathy implements itself. However, it's possible
  that some version of python might call _init() with a template, so we keep support for it.

- Start with one python version
  ([`b77c5d1`](https://github.com/justindujardin/pathy/commit/b77c5d197f3e2d728429fc341083390161fea84b))

- Try combining coverage files
  ([`246f203`](https://github.com/justindujardin/pathy/commit/246f203228146db407d3f7cdfe9c2a6a26914d0a))

- Try github actions for matrix testing
  ([`394d9ff`](https://github.com/justindujardin/pathy/commit/394d9ff52bdc67a193122aa779b40f547f2f70c3))

- Try out matrix testing on travis
  ([`89143c2`](https://github.com/justindujardin/pathy/commit/89143c23c4cd72e32990dfedee3c94e2c04d1df4))

- Try using os matrix for runs-on
  ([`1c100af`](https://github.com/justindujardin/pathy/commit/1c100af02ed73a350e3adad4328f0c3418813db7))

- Types to satisfy pyright completeness check
  ([`8143dc2`](https://github.com/justindujardin/pathy/commit/8143dc26b63eac996e9223fb88e38d6ff7fdf7c9))

- Update build badge in readme
  ([`956ebeb`](https://github.com/justindujardin/pathy/commit/956ebeba8b150f3c756f275cefb1f0def11d9ad6))

- Update deploy script to build its own venv if needed
  ([`6243893`](https://github.com/justindujardin/pathy/commit/62438934e50e609066492c018031734e6482fa36))

- Update version bump regex
  ([`ccf13d7`](https://github.com/justindujardin/pathy/commit/ccf13d7902a1d67652c0fe133c2296772e1d6364))

- Use --cov-append to combine reports
  ([`e1b572a`](https://github.com/justindujardin/pathy/commit/e1b572adedf94bc00de6a977007fca1468b86f18))

### Refactoring

- Remove legacy code paths and add tests
  ([`8bd1914`](https://github.com/justindujardin/pathy/commit/8bd1914f54f9c1b1f2940017721e8b68aecd4d80))

- some old code-paths don't appear to be reasonably reachable in Pathy, and can probably be
  attributed to left-overs from the initial port of s3path. - add better test coverage for core
  classes

- Resolve circular imports by inlining file adapter
  ([`a60006f`](https://github.com/justindujardin/pathy/commit/a60006f2c5b16f91a87083956f2e61e387257754))

- while it's perfectly fine to use lazy imports to workaround circular references, it appears to
  destroy the pylance integration and auto-imports. - move the clients.py and file.py code into base
  to make it so there is no need for lazy import workarounds.

- Test py 3.6/3.9 on ubuntu/macos
  ([`3d5e24b`](https://github.com/justindujardin/pathy/commit/3d5e24b140ab0fac7623ff742bccde1d7d3f7b7c))

- move set-build-version into deploy step

- **GCS**: Remove dead code and extra error handlers
  ([`805be85`](https://github.com/justindujardin/pathy/commit/805be8534731c7796752d33052517f72ba7564b8))

- the original implementation had a pattern of wrapping the GCS calls in try/except statements. - to
  avoid obscuring or eating valid client errors from the underlying GCS library, we no longer handle
  those cases silently, and instead let the errors bubble up to the user. In normal usage this
  shouldn't change anything. - remove the while loops from GCS scandir implementation. The python
  library doesn't use the continuation token, but exposes its own pages iterator that handles it
  transparently.

BREAKING CHANGES: The GCS client no longer handles ClientError's that occur in response to calling
  .exist() on a Path that exists but you don't have access to.

- **Pathy**: Drop rtruediv operator overload
  ([`8085eb9`](https://github.com/justindujardin/pathy/commit/8085eb94b85ef00c4924e2cd5a419e1561ff2e23))

- I couldn't construct a test-case that used the overload, and stackoverflow seems to think it's
  impractical as well:
  https://stackoverflow.com/questions/37310077/python-rtruediv-does-not-work-as-i-expect

- **Pathy.prefix**: Simplify prefix property
  ([`e6adfae`](https://github.com/justindujardin/pathy/commit/e6adfae733e6cb1b9bff72ab159d21033ac4a9b6))

- it uses Pathy.key that always joins a list of parts with _flavour.sep. Join doesn't add the value
  at the end, so the `if not key.endswith(sep)` line is unnecessary. The key will never end with sep
  - add some expectations around the property

- **tests**: Add a python version to test paths
  ([`1245aa7`](https://github.com/justindujardin/pathy/commit/1245aa71c3ef5fdfc0f38eed3e701eca6e9e146f))

- this way we can run matrix tests at the same time without the tests conflicting with each other
  trying to read/write the same blobs

### Testing

- Add expects about pathy to uri conversions
  ([`9cbf52d`](https://github.com/justindujardin/pathy/commit/9cbf52d0a398c3a11dd4e517339e7eaf48b60d0b))

- Add GCS client corner cases
  ([`6016ba2`](https://github.com/justindujardin/pathy/commit/6016ba25e8700caa254a78d7142e92a03726bf0a))

- refactor PathyScanDir subclasses to match other class names, and make them non-private members.

- Add tests for base scandir class
  ([`3157616`](https://github.com/justindujardin/pathy/commit/3157616dc5b889189551c6af10d7b99e71516153))

- More file-system client tests
  ([`bcd18af`](https://github.com/justindujardin/pathy/commit/bcd18afcd5e10bf16570847ea389122e148a72e0))

- Subfolder creation for use_fs/use_fs_cache
  ([`34deaa9`](https://github.com/justindujardin/pathy/commit/34deaa944ec97a9f64aecb6d8a7fca1d37d5be49))

- verify the sub-folder creation logic

- **pacakge**: Run tests from installed wheel
  ([`0130b5c`](https://github.com/justindujardin/pathy/commit/0130b5cc09d4db6d3ce5af2fbff1442ff6fe4473))

- this way we know the package is GTG and not just luckily running because of a file in the source
  folder that doesn't exist in the installed package.


## v0.4.0 (2021-02-15)

### Bug Fixes

- **gcs**: Stop handling DefaultCredentialsError
  ([`d4754ff`](https://github.com/justindujardin/pathy/commit/d4754ff9be5fc5ecce35ba8658097a1dd29ce5d0))

- google-cloud-storage provides a nice error message when it can't find the default credentials. Let
  it flow through to the client. - add test to ensure that if the default google creds can't be
  found, the error can be caught by the caller. - fixes #43


## v0.3.6 (2021-02-10)

### Chores

- Cleanup from review
  ([`7dd0be4`](https://github.com/justindujardin/pathy/commit/7dd0be4fef952ea81c7d0cd72b3dde3b2ccd1274))

- Cleanup from review
  ([`551ead1`](https://github.com/justindujardin/pathy/commit/551ead1af705f45a3f62b9e68a533e25f2d0f2a3))

- **ci**: Update semantic-release ([#49](https://github.com/justindujardin/pathy/pull/49),
  [`c98df80`](https://github.com/justindujardin/pathy/commit/c98df80c41649cc4fced0e89e1632d3672024f09))

- patch a dependabot vulnerability with marked < 2.0.0

### Features

- **cli**: Add "-l" flag to ls command
  ([`e47fb02`](https://github.com/justindujardin/pathy/commit/e47fb02db95b62d1060bd48d505706bcbcbbc22b))

- when provided print the size/updated time for blobs returned

- **Pathy**: Add "ls" method for quickly querying blobs with stats
  ([`bf452e7`](https://github.com/justindujardin/pathy/commit/bf452e7b658cdc4b391155264c91ddeeaed09220))

- using iterdir goes into pathlib internals and returns path objects that are (potentially)
  disconnected from their known data points (e.g. size, updated time) It's not clear how to keep the
  blob stats while using iterdir or glob methods. - add "ls" method that calls the accessor scandir
  directly and keeps the blob stat information that's returned from GCS with the blob listings. This
  avoids the need for later calling stat on each blob to provide a listing view.

- **tests**: Include tests in pypi package ([#44](https://github.com/justindujardin/pathy/pull/44),
  [`d6ad724`](https://github.com/justindujardin/pathy/commit/d6ad7244452e874e97246f38d29d0fe8e77c5b76))

* feat(tests): include tests in pypi package

- requested to support testing new versions of pathy recipes - allow overriding test buckets for GCS
  client testing

* chore: fix lint in tests

* chore: only build master branch

* chore: also build develop branch


## v0.3.5 (2021-02-02)

### Bug Fixes

- Python 3.9 compatibility ([#46](https://github.com/justindujardin/pathy/pull/46),
  [`a965f40`](https://github.com/justindujardin/pathy/commit/a965f40a086ccb305e58936813a30c35f95d5212))

* fix: python 3.9 compatibility

- a change to the way scandir is used causes a KeyError in some code paths - root cause:
  https://bugs.python.org/issue39916 - solution is to refactor scandir to use a class that can be
  used as a generator or context manager.

* chore: disable broken spacy test until thinc pr lands

* chore: make PathyScanDir iterable for py < 3.8

* chore: cleanup from review

* chore: drop old tox file

* chore: add codecov yml to disable patch coverage

- **pypi**: Add requirements.txt to distribution
  ([#45](https://github.com/justindujardin/pathy/pull/45),
  [`759cd86`](https://github.com/justindujardin/pathy/commit/759cd862be15dd1683248cdbdc0873e64f2712da))

### Chores

- **deps**: Bump ini from 1.3.5 to 1.3.8 ([#41](https://github.com/justindujardin/pathy/pull/41),
  [`36c8de9`](https://github.com/justindujardin/pathy/commit/36c8de95572047862557f4009103db1037816f78))

Bumps [ini](https://github.com/isaacs/ini) from 1.3.5 to 1.3.8. - [Release
  notes](https://github.com/isaacs/ini/releases) -
  [Commits](https://github.com/isaacs/ini/compare/v1.3.5...v1.3.8)

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>


## v0.3.4 (2020-11-22)

### Chores

- **deps-dev**: Bump semantic-release from 17.0.4 to 17.2.3
  ([#38](https://github.com/justindujardin/pathy/pull/38),
  [`6e06dbd`](https://github.com/justindujardin/pathy/commit/6e06dbdb02b1b28e38d8c4954cea763dc33a64c8))

Bumps [semantic-release](https://github.com/semantic-release/semantic-release) from 17.0.4 to
  17.2.3. - [Release notes](https://github.com/semantic-release/semantic-release/releases) -
  [Commits](https://github.com/semantic-release/semantic-release/compare/v17.0.4...v17.2.3)

Signed-off-by: dependabot[bot] <support@github.com>

Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>

### Features

- **clients**: Add set_client_params for specifying client-specific args
  ([#39](https://github.com/justindujardin/pathy/pull/39),
  [`84b9987`](https://github.com/justindujardin/pathy/commit/84b9987d4a7819ed6b9c8475523036d5809b1b2a))

* feat(clients): add set_client_params for specifying client-specific args

- useful for passing credentials and other args to the underlying bucket client library

* chore: fix lint

* test: add test for set_client_params

* chore: fix test

* test: run GCS tests during CI build

* chore: install all deps for testing

* chore: fix credentials detection

* chore: update docs

* test(clients): add recreate behavior test

* chore: use more generous wait in timestamp test

* chore: update readme snippets


## v0.3.3 (2020-11-12)

### Bug Fixes

- Path.scheme would error with schemeless paths
  ([#37](https://github.com/justindujardin/pathy/pull/37),
  [`80f0036`](https://github.com/justindujardin/pathy/commit/80f003670e9ce2515b23813fec9dfdf7a6696fb3))

- return "" from file paths as expected rather than error

### Chores

- Add BucketStat -> BlobStat to changelog
  ([`7a0bd66`](https://github.com/justindujardin/pathy/commit/7a0bd6606daab25483f4e0aabf40616c8bab3775))


## v0.3.2 (2020-11-12)

### Bug Fixes

- Upgrade smart-open to >=2.2.0,<4.0.0 ([#36](https://github.com/justindujardin/pathy/pull/36),
  [`fdf083e`](https://github.com/justindujardin/pathy/commit/fdf083eb711f225e577e9f6199a7a403b49bf2ea))

⬆️ Upgrade smart-open pin, to fix botocore requiring urllib3 < 1.26

### Chores

- Suppress ugly path open type error
  ([`d1d6e50`](https://github.com/justindujardin/pathy/commit/d1d6e50857cec83793669f01774b5bbc97edee93))

- the Path open method has a gross type that changes based on the python version. We'll use our
  specific type and deal with the consequences. :sunglasses:

### Testing

- Add a rglob + unlink test
  ([`9b80f84`](https://github.com/justindujardin/pathy/commit/9b80f84ca6431fabcda6dbfaefa3a2cc320df0ae))

- it seems like a reasonably common pattern, make sure it works like rmdir


## v0.3.1 (2020-09-26)

### Chores

- Add test for about.py to avoid failed codecov checks when releasing
  ([`976374f`](https://github.com/justindujardin/pathy/commit/976374f9ab25422ea702f64117fbcf8d84e60f55))

- if about.py changes and we don't test it, codecov is all like "wah, you didn't hit your diff
  targets because you went from 0% to 0% on about.py" :sweat_smile:

- Fix fallback type for credentials error
  ([`6c2fee7`](https://github.com/justindujardin/pathy/commit/6c2fee7fc098ce273b5651808997347286973fa0))

- Fix issue where GCS installation was not found
  ([`4059aef`](https://github.com/justindujardin/pathy/commit/4059aef7d7bad8b4ab4093b92dac3dd80750486e))

- storage var is outdated

- Fix pyright errors in gcs.py
  ([`84a8e31`](https://github.com/justindujardin/pathy/commit/84a8e31de44f4ccfd428c27ee16d8431afd0858f))

- Lint
  ([`2453f06`](https://github.com/justindujardin/pathy/commit/2453f067484a77a35d79e11657482aa2213a7b8a))

- Npm audit fix
  ([`5fa9994`](https://github.com/justindujardin/pathy/commit/5fa9994206634140d40fcc3d586f0ff7683bb516))

- Run with npx
  ([`8bcbf66`](https://github.com/justindujardin/pathy/commit/8bcbf661213707b861b128dde591143a342cbd98))

- Take two at fixing pyright errors
  ([`17b10e9`](https://github.com/justindujardin/pathy/commit/17b10e90d6efeac3214535291155167a544dc1de))

- this is pretty nice. If you don't have the packages installed, the types end up being Any
  everywhere, but if you do have them installed, you get all the correct types including
  documentation popups in the IDE and intellisense :tada:

- **deps**: Bump node-fetch from 2.6.0 to 2.6.1
  ([`0d46e72`](https://github.com/justindujardin/pathy/commit/0d46e72571df3925c601f92579c343e4db4f437e))

Bumps [node-fetch](https://github.com/bitinn/node-fetch) from 2.6.0 to 2.6.1. - [Release
  notes](https://github.com/bitinn/node-fetch/releases) -
  [Changelog](https://github.com/node-fetch/node-fetch/blob/master/docs/CHANGELOG.md) -
  [Commits](https://github.com/bitinn/node-fetch/compare/v2.6.0...v2.6.1)

Signed-off-by: dependabot[bot] <support@github.com>

### Features

- Update smart-open to 2.2.0 for minimal deps
  ([`4b3e959`](https://github.com/justindujardin/pathy/commit/4b3e959ce1c4c491cb291935e8d47ac537b72485))

- to get GCS support, use `pip install pathy[gcs]`

- **ci**: Add pyright check to lint step
  ([`10ce34d`](https://github.com/justindujardin/pathy/commit/10ce34d13ddc99232b3ce7681db27f561d51c87b))


## v0.3.0 (2020-09-04)

### Chores

- Add auto format and lint scripts
  ([`b54d141`](https://github.com/justindujardin/pathy/commit/b54d141c75f24a2b2fdcd85cc9ba91e9917d9d8f))

- Add codecov script
  ([`cece852`](https://github.com/justindujardin/pathy/commit/cece85243ec0456debade6874d3be2f3f42d16a7))

- Add coverage badge to readme
  ([`70d96b7`](https://github.com/justindujardin/pathy/commit/70d96b707f362a70d4ab52e1791bf9ba9bca9879))

- Add semantic PR title linting github action
  ([`ac3d0ab`](https://github.com/justindujardin/pathy/commit/ac3d0ab0327422c00df1c59b2010a711643f43bf))

- Cleanup from review
  ([`5d7cb8a`](https://github.com/justindujardin/pathy/commit/5d7cb8afa8f0ae76fe49718a907f9fef604831c8))

- Drop github action for semantic pr titles
  ([`71defad`](https://github.com/justindujardin/pathy/commit/71defad27550bdfc0753bbd36c4d5305956fc5a0))

- really the title is secondary to the commits in the PR. We'll continue to use the Semantic PR
  github app as long as it works

- Drop PathType variable
  ([`3168af4`](https://github.com/justindujardin/pathy/commit/3168af4566ef79d55f1b821c34d57b312fd34395))

- since consolidating the Pathy class in the base.py file, there's no need to TypeVars, we can just
  use a forward ref to Pathy itself :tada:

- Fix extras in setup.py
  ([`35569a3`](https://github.com/justindujardin/pathy/commit/35569a356f54ffe15299d13c2bce95ec2839cb5a))

- Fix tests without google-auth installed
  ([`78f5361`](https://github.com/justindujardin/pathy/commit/78f5361f12e7cabb0a77e79bf08226816802fc1a))

- Fix the remaining mypy errors
  ([`968a226`](https://github.com/justindujardin/pathy/commit/968a226507498bd319dd64f61c25a6dd4df627f6))

- in some cases the mypy errors are too uptight about subclasses and their types. When that happens
  we silence the error and provide the expected subclass type.

- Fix travis lint invocation
  ([`96fa4ea`](https://github.com/justindujardin/pathy/commit/96fa4ea1db3d6d2f4986569fb73cfffaa59f8f74))

- Misc cleanup
  ([`d6e7e92`](https://github.com/justindujardin/pathy/commit/d6e7e92798b736e1a8ae5b9c02157c06982f2c33))

- Remove isort test from lint script
  ([`c06f6ab`](https://github.com/justindujardin/pathy/commit/c06f6abbf0bdae38f270fa3781847dc906779779))

- we black format last, so the order/indent could be changed.

- Update docs
  ([`8a78712`](https://github.com/justindujardin/pathy/commit/8a787125df45f17f9f3d9a617ced20210559fe76))

- Update readme
  ([`a537fa9`](https://github.com/justindujardin/pathy/commit/a537fa98c619021d0a2815ff329c7af8e2ecefee))

restore the credits to s3path library

- Use venv when linting
  ([`3b5aef3`](https://github.com/justindujardin/pathy/commit/3b5aef3b96a05e742ed297984e4a2617f73ad0e0))

### Documentation

- Add section about semantic version to readme
  ([`c7f6d19`](https://github.com/justindujardin/pathy/commit/c7f6d19b1b3e264014ab8c51800dd1c6e8c6aa81))

### Features

- Add get_client/register_client for supporting multiple services
  ([`747815b`](https://github.com/justindujardin/pathy/commit/747815b46e1e3cd61e6e69d04b52f5f5958ed373))

Adds a simple registry of known schemes and their mappings to BucketClient subclasses. There's a
  hardcoded list of built-in services, and (in theory) you can register more dynamically.

I think I prefer to hardcode and include most of the known services, and lazily import them so you
  only need their packages when you actually use them. The hope is that this lets the strong typings
  flow through to the clients (because they can be statically inspected). If we can't get specific
  types flowing through nicely, maybe it's okay to do more of a dynamic import style registration.

BREAKING CHANGE use_fs, get_fs_client, use_fs_cache, get_fs_cache, and clear_fs_cache moved from
  pathy.api to pathy.clients

- **ci**: Add lint check before testing
  ([`2633480`](https://github.com/justindujardin/pathy/commit/263348028fe5c217163632d9fd002cd7f5b5c77c))

- **GCS**: Print install command when using GCS without deps installed
  ([`d8dbcd4`](https://github.com/justindujardin/pathy/commit/d8dbcd41d1e813090cad906c81df95880ae7289c))

- make the assertion prettier :sunglasses:

### Refactoring

- Add BasePathy class to bind PathType var to
  ([`796dd40`](https://github.com/justindujardin/pathy/commit/796dd407fca72c5297914e597f3221fdbcd9e95e))

BREAKING CHANGE: This renames the internal GCS/File adapter classes by removing the prefix Client.

ClientBucketFS -> BucketFS ClientBlobFS -> BlobFS ClientBucketGCS -> BucketGCS ClientBlobGCS ->
  BlobGCS

- Combine api/client with base.py
  ([`a522461`](https://github.com/justindujardin/pathy/commit/a52246141b52440b9f9b3ace46d0a451af268be6))

- this makes the Pathy type accessible where it otherwise would not be for TypeVars.

- **pypi**: Move gcs dependencies into pathy[gcs] extras
  ([`c034dd1`](https://github.com/justindujardin/pathy/commit/c034dd1429e7745d1f8e0a661f2c4499ffd72d73))


## v0.2.0 (2020-08-22)

### Chores

- Add BucketStat to docs
  ([`9a7f8d8`](https://github.com/justindujardin/pathy/commit/9a7f8d819a27e8282abc5e14ed9c62a810cdc038))

- Fix ci build badge
  ([`aacb9f7`](https://github.com/justindujardin/pathy/commit/aacb9f7d46526b4643fe978333d6700f06db15c9))

- Update docs
  ([`e3a2c49`](https://github.com/justindujardin/pathy/commit/e3a2c49939b4fe65dd3ef112ae16f6c2cdd9aedf))

- **deps**: Bump lodash from 4.17.15 to 4.17.19
  ([`18938a2`](https://github.com/justindujardin/pathy/commit/18938a216c69b2611b7b7edf82809af66f39f6b2))

Bumps [lodash](https://github.com/lodash/lodash) from 4.17.15 to 4.17.19. - [Release
  notes](https://github.com/lodash/lodash/releases) -
  [Commits](https://github.com/lodash/lodash/compare/4.17.15...4.17.19)

Signed-off-by: dependabot[bot] <support@github.com>

- **deps**: Bump npm from 6.14.2 to 6.14.6
  ([`83b07f2`](https://github.com/justindujardin/pathy/commit/83b07f208bd7d1146123c1576fab5accd664a02b))

Bumps [npm](https://github.com/npm/cli) from 6.14.2 to 6.14.6. - [Release
  notes](https://github.com/npm/cli/releases) -
  [Changelog](https://github.com/npm/cli/blob/latest/CHANGELOG.md) -
  [Commits](https://github.com/npm/cli/compare/v6.14.2...v6.14.6)

Signed-off-by: dependabot[bot] <support@github.com>

### Features

- **build**: Use husky to auto update docs when code changes
  ([`5a32357`](https://github.com/justindujardin/pathy/commit/5a32357db47f003fb3ebc6345d7fa4cee829fd99))

- **README**: Generate API and CLI docs
  ([`0213d2f`](https://github.com/justindujardin/pathy/commit/0213d2f7028c08d40d863d1cc123e7d55ff1c89f))

### Refactoring

- Rename PureGCSPath to PurePathy
  ([`5632f26`](https://github.com/justindujardin/pathy/commit/5632f264ed5d22b54b1c284ca1d79d2e248c5fd3))

Be more consistent with the Pathy naming.

BREAKING CHANGE: PureGCSPath is now PurePathy

### Breaking Changes

- Puregcspath is now PurePathy


## v0.1.3 (2020-06-28)

### Features

- Upgrade typer support
  ([`e481000`](https://github.com/justindujardin/pathy/commit/e4810004eff21a605626d30cd717983787a6a8c6))

- allow anything in range >=0.3.0,<1.0.0


## v0.1.2 (2020-05-23)

### Bug Fixes

- Path.owner() can raise when using filesystem adapter
  ([`2877b06`](https://github.com/justindujardin/pathy/commit/2877b06562e4bb1d4767e9c297e2aee2fc1284ad))

- catch the error and return a None owner


## v0.1.1 (2020-04-24)

### Features

- **cli**: Add -r and -v flags for safer usage
  ([`a87e36f`](https://github.com/justindujardin/pathy/commit/a87e36fbc13a705c1f7f9ed7909ff6c9fe8e494e))

- rm will fail if given a directory without the -r flag (similar to unix rm) - rm will print the
  removed files/folders when given the -v flag


## v0.1.0 (2020-04-24)

### Chores

- Fix bad entry_point in setup.py
  ([`25c58a3`](https://github.com/justindujardin/pathy/commit/25c58a312131bbc31c17c5fc7f37905074ded5d9))

### Features

- Add FluidPath and GCSPath.fluid method
  ([`3393226`](https://github.com/justindujardin/pathy/commit/3393226bc7f390f696d109bfac5f44e59a8b5151))

GCSPath wants to work with many kinds of paths, and it's not always clear upfront what kind of path
  a string represents. If you're on a local file system, the path "/usr/bin/something" may be
  totally valid, but as a GCSPath it isn't valid because there's no service scheme attached to it,
  e.g. "gs://bucket/usr/bin/something"

FluidPath is a Union of pathlib.Path and GCSPath which allows type-checking of the paths without
  needing explicit knowledge of what kind of path it is, until that knowledge is needed.

*note* I originally thought of using "UnionPath" instead of "FluidPath" but the intellisense for
  completing "GCSPath.union" was very crowded, and a helper should be easy to type with completion.

- **cli**: Add ls [path] command
  ([`17cab1d`](https://github.com/justindujardin/pathy/commit/17cab1d8b96d92ca79e18512ac7e8a42aa136066))

- prints the full paths of files found in the location

- **cli**: Add pathy executable with cp and mv commands
  ([`98760fc`](https://github.com/justindujardin/pathy/commit/98760fcfc0cb62891b7f2aac81a74fef088fdf78))

- add "pathy" entry point to the gcspath package - add Typer requirement - add typer CLI app for
  copying and moving files - basic test

- **cli**: Add rm [path] command
  ([`31cea91`](https://github.com/justindujardin/pathy/commit/31cea9156d99d9d465569c20c566943d4238c5dd))

- removes files or folders - add tests

- **pathy**: Rename library to be more generic
  ([`c62b14d`](https://github.com/justindujardin/pathy/commit/c62b14da2aba25024af647e29df09ee57a13f6bd))

- it does more than just GCS at this point

### Refactoring

- Construct bucket paths with service prefixes
  ([`8a2fb27`](https://github.com/justindujardin/pathy/commit/8a2fb27b817396d0b07047d154c6456fb85578dd))

BREAKING CHANGES: GCSPaths must include a path scheme

Before GCSPath would convert `/bucket-name/file` into `gs://bucket-name/file` internally. This leads
  to ambiguity *(thanks @honnibal) when dealing with regular file-system paths and bucket paths
  together. Does the path `/foo/bar` point to an absolute file path or a GCS bucket named foo?

Now paths **must be** constructed with a path scheme. This allows GCSPath to deal with both types of
  paths, and is needed for the CLI apps to come.

### Testing

- **cli**: Add tests for cp/mv files and folders
  ([`7b85ca1`](https://github.com/justindujardin/pathy/commit/7b85ca15e9f6deee941e934d42d57562aab7e5d9))


## v0.0.17 (2020-04-17)

### Bug Fixes

- Do not de/compress opened files based on extension
  ([`22d14e7`](https://github.com/justindujardin/pathy/commit/22d14e7d4919f16ca54bf28e685c221f7c96f8d3))

- the streaming library we use smart_open does automatic de/compression if it sees a recognized file
  extension. We don't want that behavior here.


## v0.0.16 (2020-04-16)

### Features

- **typing**: Expose library python types to mypy
  ([`53cf348`](https://github.com/justindujardin/pathy/commit/53cf34845399e1d31538dc02e462d7e02bcd32a6))

- add py.typed file and include in the package - overload / operator to provide a definitive GCSPath
  return type when building paths


## v0.0.15 (2020-04-16)

### Bug Fixes

- **requirements**: Remove typer dependency
  ([`08e8fa0`](https://github.com/justindujardin/pathy/commit/08e8fa0baa186b710a6adf2205b0a51bbd39fe37))

- this was an idea for a feature, but it's not used ATM


## v0.0.14 (2020-04-16)

### Bug Fixes

- **iterdir**: Don't return empty results
  ([`2a8b870`](https://github.com/justindujardin/pathy/commit/2a8b870c2ca232431c65808050363e8faff60ba2))

- when iterating a pipstore folder, the source folder was returned with an empty name


## v0.0.13 (2020-04-16)

### Bug Fixes

- **to_local**: Issue where files without extensions would not be cached
  ([`3d543a8`](https://github.com/justindujardin/pathy/commit/3d543a88a81604d13f8e401422d59803d9bb3943))

- oops :sweat_smile:


## v0.0.12 (2020-04-15)

### Bug Fixes

- Recursion error when copying blob folders
  ([`8b6e01c`](https://github.com/justindujardin/pathy/commit/8b6e01c3e8c35a78deee60d45563b27b7a732e9a))


## v0.0.11 (2020-04-15)

### Features

- **to_local**: Support caching folders
  ([`cc56f6e`](https://github.com/justindujardin/pathy/commit/cc56f6eab21f850f0521013749589ad0736e261d))

- when given a path to cache that does't point to a blob, rglob the blobs under it and cache them. -
  this is useful for things like spaCy models that are folders with a bunch of blobs that need to be
  cached.


## v0.0.10 (2020-04-14)

### Chores

- More cleanup
  ([`af473da`](https://github.com/justindujardin/pathy/commit/af473da01c00186c884052d42a39f64d0f567cfc))

- Restructure tests to map to source files
  ([`4f271bf`](https://github.com/justindujardin/pathy/commit/4f271bf8e94e175794cf59ae9e12ab7874854d9c))

- the test names didn't correspond to files and it made it difficult to know where a particular test
  might be.

### Features

- Add `use_fs_caching` and `GCSPath.to_local` for caching
  ([`2894360`](https://github.com/justindujardin/pathy/commit/2894360d48e3ac4b28ecb4627eb562f9e65b3c93))

- use_fs_cache sets a folder for downloading and caching files locally. This is useful for when you
  want to avoid downloading large files multiple times, or when you need to call into a third-party
  library that requires a file that exists on disk.


## v0.0.9 (2020-04-08)

### Features

- Add `resolve` method
  ([`7cebc69`](https://github.com/justindujardin/pathy/commit/7cebc69bfc88b1a522defdce1637f5159c37def6))

- converts path to absolute and removes relative parts


## v0.0.8 (2020-04-08)

### Features

- Allow passing GCSPath to spacy.Model.to_disk
  ([`1d628cb`](https://github.com/justindujardin/pathy/commit/1d628cb8c5056683590d9f2403f1482e2a310971))

- add test that exports a blank model then enumerates its files from the GCSPath

- **use_fs**: Allow passing root folder as Path
  ([`3635152`](https://github.com/justindujardin/pathy/commit/36351525bf84001ed4f9b0b7abf842f8e27ef1f0))


## v0.0.7 (2020-03-30)

### Bug Fixes

- **gcs**: Gracefully handle invalid gcs client case
  ([`529f630`](https://github.com/justindujardin/pathy/commit/529f63026abe1b11c3336febb152a030e28a85ef))

- by default ignore default client credential errors until the accessor.client prop is referenced. -
  this allows you to call `use_fs` after the initial module import


## v0.0.6 (2020-03-30)

### Chores

- Update changelog [skip-ci]
  ([`1bfab7c`](https://github.com/justindujardin/pathy/commit/1bfab7c102441a9f91408039a33f890af33202a6))

### Features

- Add github releases for each pypi version
  ([`66dbed8`](https://github.com/justindujardin/pathy/commit/66dbed851346372ab84080f027113aba054452af))


## v0.0.5 (2020-03-30)

### Bug Fixes

- Generating changelog
  ([`ef43ed1`](https://github.com/justindujardin/pathy/commit/ef43ed11a140ed3cfaba2e7d72b7c01c7275c8d6))


## v0.0.4 (2020-03-30)

### Chores

- Disable GCS tests on CI
  ([`821803f`](https://github.com/justindujardin/pathy/commit/821803f3bd28de8851ac44c5c648f83e8808cf3b))

### Features

- Support unlink path operation
  ([`d97d636`](https://github.com/justindujardin/pathy/commit/d97d63628007c24a44361ffd1ee218651fb781d8))

- for removing single blobs


## v0.0.3 (2020-03-30)

### Chores

- Add long_description back
  ([`fc7570c`](https://github.com/justindujardin/pathy/commit/fc7570c61c73bbdc3235e28eda613eadebdf1281))

- Add parametrize for remaining tests
  ([`a6b88e8`](https://github.com/justindujardin/pathy/commit/a6b88e84bfd0ec2d3a1445c32a07d78bb767e759))

- Begin fixing tests for FS adapter
  ([`7569051`](https://github.com/justindujardin/pathy/commit/756905180eb5cff83876d772322831bcaa8b012d))

- openining blobs requires a hook to create intermediate folders. So if you create a blob at
  `/bucket/some/subfolder/foo.txt` the client can mkdir the path before creating the file. - move
  the `open` method into BucketClient to support the hook above. - create testing buckets if they
  don't already exist using a pytest fixture

- Better usage of ClientBucket
  ([`689b4ce`](https://github.com/justindujardin/pathy/commit/689b4cef67490787bdd9fb35cf169666623337a1))

- Cleanup code
  ([`24bae93`](https://github.com/justindujardin/pathy/commit/24bae9345648fbda4c0fd53075d1e2f8447a6298))

- Drop wip test fixture for fs
  ([`48ed2b7`](https://github.com/justindujardin/pathy/commit/48ed2b7907e582db47406440167d83e4992cc030))

- Extract gcs client from GCSPath
  ([`df8d66d`](https://github.com/justindujardin/pathy/commit/df8d66d45325a4dc5f99519028f1837fec80a9c0))

- Add `BucketClient` class that can be implemented by any client that supports read/write bucket
  APIs. - Add `BucketClientGCS` for the GCS service

- Fix more fs+gcs test suite behavior differences
  ([`790e0d7`](https://github.com/justindujardin/pathy/commit/790e0d7fdd764914cbcdc68ba264a1c287e6a512))

- add is_dir and rmdir to BucketClient class

- Move dir entry and stat to client.py
  ([`81a0b49`](https://github.com/justindujardin/pathy/commit/81a0b49f889de9080a21699be801808c3a1a1b8b))

- Untangle bucket clients usage from GCS more
  ([`c12d2dd`](https://github.com/justindujardin/pathy/commit/c12d2dd668dbab00c742e9a970dd6332bc2aa01e))

- use a sanitized Client interface. - remove _generate_prefix and _bucket_name methods from GCSPath
  class. add `prefix` and `bucket_name` properties to PureGCSPath. - add scandir to the BucketClient
  interface

### Features

- Add filesystem bucket adapter
  ([`1c72f47`](https://github.com/justindujardin/pathy/commit/1c72f475fde8de1c6cb3af23d63b793722fe82e2))

- buckets are folders created as children of some root path - TODO: how to set the root path? Start
  with a built-in path like the spaCy data path. This should work with matt's want for registered
  paths on the command line.

- Use_fs stores buckets on the file-system
  ([`f717280`](https://github.com/justindujardin/pathy/commit/f7172806d0ae3e408aafc12fe7526b9852ce8b36))

- this bypasses the use of GCS and enables better developer and testing experiences when working
  with the library

- **gcs**: Use smart_open for streaming files
  ([`e557ab9`](https://github.com/justindujardin/pathy/commit/e557ab9e3bc7c0edcb02333fe8ea6be760c152dc))

- remove gs-chunked-io and GCSReadable/GCSWritable classes. - move code to a module folder rather
  than a single-file package

### Refactoring

- Add abstractions for Bucket/Blob in GCS
  ([`19c4505`](https://github.com/justindujardin/pathy/commit/19c4505aaf20eb4d244198dd82e7b4344146ef64))

### Testing

- Add pytest parametrize for gcs/fs adapters
  ([`9863ed2`](https://github.com/justindujardin/pathy/commit/9863ed24b97d746c01e933116fa26c8bbaa4a794))

- only a few tests right now - refactor exists() to delegate to adapter specific logic. The use of
  listblobs for exists and the associated filtering logic only makes sense when you're trying to get
  a bucket-based system like GCS to act like it has folders. For the FS adapter we can just check if
  the full_path on the system exists with the base pathlib.Path class.

- Fix remaining GCS/FS adapter differences
  ([`b18a7ed`](https://github.com/justindujardin/pathy/commit/b18a7ed120c707fa783c484074d0c62c267b5cd3))

- all tests pass with GCS/FS adapters now


## v0.0.2 (2020-03-18)

### Bug Fixes

- **tests**: Enable unit tests on ci
  ([`dd56011`](https://github.com/justindujardin/pathy/commit/dd560116409e82652e61a6e40ceebd27da0f3783))

- can't run the path tests yet, so coverage is terrible. - skip them for now


## v0.0.1 (2020-03-18)

### Bug Fixes

- **ci**: Remember to trigger semantic-release
  ([`dcff020`](https://github.com/justindujardin/pathy/commit/dcff0207be0f3677f8d5c232918844c58e2a81fe))

### Chores

- Add iterdir and open for read/write streams
  ([`d1648b0`](https://github.com/justindujardin/pathy/commit/d1648b0c9855eca075d9f3d0b671e9e081ac67f1))

- annoyingly GCS doesn't support file-like objects:
  https://github.com/googleapis/python-storage/issues/29 - use a small library for doing file-like
  object support for GCS: https://github.com/xbrianh/gs-chunked-io

- Cleanup hardcoded buckets in tests
  ([`4e568f2`](https://github.com/justindujardin/pathy/commit/4e568f2f873618dad4e2e9db639fc3bfbc00b53e))

- Disable tests
  ([`746f478`](https://github.com/justindujardin/pathy/commit/746f4785228d046851fbfe8afb732dafe9291296))

- Fix path in set-build-version
  ([`a87b2dc`](https://github.com/justindujardin/pathy/commit/a87b2dcfbec823c1d6545f807b6557a9b459cf5b))

- Fix repo typo
  ([`085543d`](https://github.com/justindujardin/pathy/commit/085543deb8dbe649cb8d52eb53d0f28b6bcd12c1))

- Fix setup.py readme link
  ([`b1744fa`](https://github.com/justindujardin/pathy/commit/b1744fa2d0dcb3597e238086abfff3f2cb637feb))

- Fix typo in deploy script
  ([`b5a3bc6`](https://github.com/justindujardin/pathy/commit/b5a3bc61ce2708f6a53441dce1aeca19eb90c269))

- Implement and tests for glob, rglob, is_dir, is_file
  ([`a266706`](https://github.com/justindujardin/pathy/commit/a2667065cfcd7f5f1e8c13baeac797710d9de98f))

- Kick build
  ([`641bbac`](https://github.com/justindujardin/pathy/commit/641bbac31ec35b18c0c67286651487243cf28f04))

- Kick build
  ([`69b86e3`](https://github.com/justindujardin/pathy/commit/69b86e32f859f936217304f11cf0bb518e7bea29))

- More e2e tests passing
  ([`525609e`](https://github.com/justindujardin/pathy/commit/525609e082a4ae1fbba9c3af858355eaae7c3cfa))

- Readme cleanup
  ([`7974f11`](https://github.com/justindujardin/pathy/commit/7974f1150111c41ec8d2ca131e2a076f04fdcbc7))

- Set py version in travis script
  ([`95455d6`](https://github.com/justindujardin/pathy/commit/95455d681fd508d4d4c362faa6fabc390ec325dd))

- Wip GCS port of https://github.com/liormizr/s3path
  ([`1196a6a`](https://github.com/justindujardin/pathy/commit/1196a6a759b7eb52e7baea3a9d0e4069f8cf56a6))

- **ci**: Install node 10.18 for semantic-release
  ([`4a01541`](https://github.com/justindujardin/pathy/commit/4a0154108c114cfe791398ac4e37396e8b02c99e))

### Features

- **ci**: Add semantic-release
  ([`9757b3c`](https://github.com/justindujardin/pathy/commit/9757b3c2a455c205452f5d0ff90e2b74950dd0e1))

### Testing

- Add rmdir and mkdir tests
  ([`6d2470d`](https://github.com/justindujardin/pathy/commit/6d2470d0166ace0b4945b625f96633b89ad38c49))

- Rename/replace with files and folders
  ([`496631d`](https://github.com/justindujardin/pathy/commit/496631db03bd8c946a44f0bbc6e98d223d82cfa2))

- works in-bucket and across buckets
