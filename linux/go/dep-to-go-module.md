## Link
https://stackoverflow.com/questions/55664630/how-do-i-migrate-from-dep-to-go-modules

## Migrating from Dep to Go Modules is very easy.
- Run `go version` and make sure you're using version 11 or later.
- Move your code outside of `GOPATH` or set `export GO111MODULE=on`.
- `go mod init [module path]`: This will import dependencies from `Gopkg.lock`.
- `go mod tidy`: This will remove unnecessary imports, and add indirect ones.
- `rm -rf vendor/`: Optional step to delete your vendor folder.
- `go build`: Do a test build to see if it works.
- `rm -f Gopkg.lock Gopkg.toml`: Delete the obsolete files used for Dep.
- Go has imported my dependencies from `Dep` by reading the `Gopkg.lock` file and also created a `go.mod` file.

If you want to keep your vendor folder:
- Run `go mod vendor` to copy your dependencies into the vendor folder.
- Run `go build -mod=vendor` to ensure go build uses your vendor folder.
