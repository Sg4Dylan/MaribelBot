export GOOS=linux
export GOARCH=amd64
export CC="zig cc -target x86_64-linux-gnu.2.17"
export CXX="zig c++ -target x86_64-linux-gnu.2.17"
go build -o Maribel -ldflags="-s -w" ./cmd/bot
