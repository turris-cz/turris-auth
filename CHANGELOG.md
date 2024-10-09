# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2024-10-09

### Added

-   Added extend session functionality

## [1.1.0] - 2024-09-19

### Added

-   Added & updated Weblate translations
-   Added project, version, copyright information to POT file generation

### Changed

-   Refactored login page and styles to match latest changes in our theme

### Removed

-   Removed unused resources and updated dynamic configuration

## [1.0.0] - 2024-05-29

### Changed

-   add tests, lint and publishing for gitlab CI
-   migrate to hatchling instead of setuptools

### Fixed

-   fix Content-type header to use application/json in wsgi.py

## [0.4.3] - 2023-05-24

### Changed

-   change the name of LuCI cookies to adapt to the latest version of LuCI in TOS 7.0
-   cookie: Drop compatibility for the 'samesite' cookie attribute for Python 3.7 and older.

## [0.4.2] - 2022-10-06

### Fixed

-   fix redirect to any origin on redirect

## [0.4.1] - 2022-08-30

### Fixed

-   fix empty cookie removal on logout

## [0.4.0] - 2022-05-09

### Added

-   argument `--luci-login` that enables login not only to Turris Authenticator
    but also to LuCI in one go

## [0.3.1] - 2022-02-16

### Changed

-   updated translations

## [0.3.0] - 2022-01-19

### Added

-   translations
-   automatic login if password is not set (required for initial setup)
-   link to HTTPS documentation on login page

### Changed

-   replaced theme with Turris Bootstrap theme

### Fixed

-   set cookie timeout to documented 10 minutes instead of 10 hours

## [0.2.0] - 2021-11-02

### Added

-   alert about insecure connection
-   opportunistic redirect to HTTPS from HTTP

### Changed

-   magnet module is switched to fastcgi and everything is migrated to use that
-   server now returns 401 error code when X-Requested-With header is send
-   project is now named only turris-auth as it no longer is essentially dependent
    on Lighttpd
-   website style migrated to the bootstrap version 4.6.0

## [0.1.1] - 2021-09-08

### Fixed

-   easy to exploit shell escape

## [0.1.0] - 2021-08-30

### Added

-   initial version of turris-auth with support for current Foris password
