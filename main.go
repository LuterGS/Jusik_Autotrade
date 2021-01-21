package main

import (
	test "./src"
	"runtime"
)

/*
https://github.com/LuterGS/Jusik_Autotrade Python 기반의 프로그램을 Go로 포팅한 프로젝트입니다.
Python의 생산성을 이용해 빠르게 알고리즘을 기획했으며, 이제 Go로 포팅함으로써 효율성을 잡을 예정입니다.


*/

func main() {

	runtime.GOMAXPROCS(runtime.NumCPU())

	test.Test()

	// TODO : Buy, Sell Jusik을 테스트해봐야 함

	test.Mainer()

}
