# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased]
### Added
- Added new databases from *IAA* and from *Transportes*.

### Fixed
- Project files and folders reorganization.
- Code modularization.

## [1.2.1] - 2017-05-11

### Added
- Added an independent app *GA_OD_Core Validator* to validate URLs from the API.
- Added new logs related with DB connections.


## [1.2.0] - 2016-10-20

### Added
- New CHANGELOG file necessary to follow the changes of the application in the new versioning system.
- Initial version of the new versioning system of the application.
- New functionality to query Google Analytics views.
- New fields *_page* and *_pageSize* to paginate the queries of the *preview* and *download* methods. *_pageSize* limits the registers number returned by the query and *_page* limits the number of page returned.
- New error control to avoid status code 500 and similar.




## [1.1.0] - 2016-09-20

### Changed
- Normal log mode changed to separated log mode in several files with a max size of 5MB in every log file.
- Changed the log in the PRO environment to avoid to write it in the screen.
- Modified some database connections depending to the environment variable to simplify the deployment in different environments.

### Removed
- Commented code cleaned.

### Fixed
- Several spanish comments translated to english.
- CSV files creation improved.
- Improved logging to show more information in the event of an error.
- Table data character encoding errors fixed.


[Unreleased]: https://github.com/aragonopendata/GA_OD_Core/compare/master...develop

[1.2.1]: https://github.com/aragonopendata/GA_OD_Core/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/aragonopendata/GA_OD_Core/compare/v1.1.1...v1.2.0
[1.1.0]: https://github.com/aragonopendata/GA_OD_Core/releases/tag/v1.1.0