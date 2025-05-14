window.BENCHMARK_DATA = {
  "lastUpdate": 1747250263447,
  "repoUrl": "https://github.com/procrastinate-org/procrastinate",
  "entries": {
    "Procrastinate Benchmarks": [
      {
        "commit": {
          "author": {
            "email": "kai.schlamp@gmail.com",
            "name": "Kai Schlamp",
            "username": "medihack"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "6d8fc857e7cc68b022328011db7a54a1ce44b856",
          "message": "Merge pull request #1347 from procrastinate-org/benchmark\n\nAdd some very simple benchmarks",
          "timestamp": "2025-03-18T21:20:35+01:00",
          "tree_id": "727c6dd830919de3b93ae81f79feacfe76d6d62e",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/6d8fc857e7cc68b022328011db7a54a1ce44b856"
        },
        "date": 1742331003802,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2616658567821434,
            "unit": "iter/sec",
            "range": "stddev: 0.1152565744897831",
            "extra": "mean: 3.8216678794000076 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.47506395869924734,
            "unit": "iter/sec",
            "range": "stddev: 0.06710144109600152",
            "extra": "mean: 2.104979722600001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2341241642285222,
            "unit": "iter/sec",
            "range": "stddev: 0.18981403416270898",
            "extra": "mean: 4.271237884799996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2630603679021889,
            "unit": "iter/sec",
            "range": "stddev: 0.08168057946557436",
            "extra": "mean: 3.801408809600008 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "89437c3e55488fd4cbab0f79e8b11f774e1d72ee",
          "message": "Merge pull request #1348 from ticosax/marker\n\nAdd missing pytest's marker description",
          "timestamp": "2025-03-20T15:51:35+01:00",
          "tree_id": "e353fe3dec6f37ad3e43f4c17a44bf7adbe4c606",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/89437c3e55488fd4cbab0f79e8b11f774e1d72ee"
        },
        "date": 1742482448853,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.24206059190403414,
            "unit": "iter/sec",
            "range": "stddev: 0.1310508415292861",
            "extra": "mean: 4.131197036800001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.41989419307428905,
            "unit": "iter/sec",
            "range": "stddev: 0.10387723576494383",
            "extra": "mean: 2.381552344600004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2260540559547511,
            "unit": "iter/sec",
            "range": "stddev: 0.18877959943789266",
            "extra": "mean: 4.423720670599994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.23376518741746832,
            "unit": "iter/sec",
            "range": "stddev: 0.1586201249188444",
            "extra": "mean: 4.277796925399997 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kai.schlamp@gmail.com",
            "name": "Kai Schlamp",
            "username": "medihack"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b1a580059223b9023480fc9a6e44930c1149104c",
          "message": "Merge pull request #1350 from ticosax/revert-1348-marker\n\nRevert \"Add missing pytest's marker description\"",
          "timestamp": "2025-03-21T18:55:06+01:00",
          "tree_id": "727c6dd830919de3b93ae81f79feacfe76d6d62e",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/b1a580059223b9023480fc9a6e44930c1149104c"
        },
        "date": 1742579842157,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2868919953721058,
            "unit": "iter/sec",
            "range": "stddev: 0.13971818595305988",
            "extra": "mean: 3.4856322801999964 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5410401162196153,
            "unit": "iter/sec",
            "range": "stddev: 0.02800110505627549",
            "extra": "mean: 1.8482917810000004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.26215662542216805,
            "unit": "iter/sec",
            "range": "stddev: 0.12133553093485434",
            "extra": "mean: 3.8145135504000107 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.29028601386472874,
            "unit": "iter/sec",
            "range": "stddev: 0.05489589208847261",
            "extra": "mean: 3.444878334600003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "eff5503357eef6a4a891e9a3f612fa46afd68229",
          "message": "Merge pull request #1330 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-03-22T10:10:04Z",
          "tree_id": "f3a8960f4589bc2c6a47d7b5f3baac5d15de3480",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/eff5503357eef6a4a891e9a3f612fa46afd68229"
        },
        "date": 1742638348468,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2653586730928144,
            "unit": "iter/sec",
            "range": "stddev: 0.17648834102585859",
            "extra": "mean: 3.768484324800005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4668544909492173,
            "unit": "iter/sec",
            "range": "stddev: 0.035204956497006994",
            "extra": "mean: 2.1419950314000005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2513882897688651,
            "unit": "iter/sec",
            "range": "stddev: 0.0639227290336985",
            "extra": "mean: 3.9779100327999912 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2683362177188724,
            "unit": "iter/sec",
            "range": "stddev: 0.05714533502673422",
            "extra": "mean: 3.7266680156000005 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "a8cdeb8ebdfe80698273b70028a841165b5fe49d",
          "message": "Merge pull request #1351 from procrastinate-org/fix-doc\n\ndoc fix",
          "timestamp": "2025-03-22T11:22:09+01:00",
          "tree_id": "9cdef3a985ef3e75c58343d777f3bcf934a32d9a",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/a8cdeb8ebdfe80698273b70028a841165b5fe49d"
        },
        "date": 1742639065926,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.28112922530521384,
            "unit": "iter/sec",
            "range": "stddev: 0.12847085095018168",
            "extra": "mean: 3.557083042200003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4998605620467352,
            "unit": "iter/sec",
            "range": "stddev: 0.04292098411476091",
            "extra": "mean: 2.0005579073999913 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2555860328722867,
            "unit": "iter/sec",
            "range": "stddev: 0.12652022180730443",
            "extra": "mean: 3.9125768680000137 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2790794177329405,
            "unit": "iter/sec",
            "range": "stddev: 0.06033815219751311",
            "extra": "mean: 3.583209425199999 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "b547e471091cf01aa1906bb4d6ce015ed5ddca6d",
          "message": "Merge pull request #1354 from procrastinate-org/fix-flaky-test\n\nAdjust sleep times in test_stop_worker_aborts_sync_jobs_past_shutdown_graceful_timeout",
          "timestamp": "2025-03-22T11:52:23+01:00",
          "tree_id": "86a0beb9df99ccfe9022affed124814899889f32",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/b547e471091cf01aa1906bb4d6ce015ed5ddca6d"
        },
        "date": 1742640891462,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26602756069279726,
            "unit": "iter/sec",
            "range": "stddev: 0.1368010302542491",
            "extra": "mean: 3.759009019199999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4940313281499021,
            "unit": "iter/sec",
            "range": "stddev: 0.02039635109349924",
            "extra": "mean: 2.0241631310000114 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24725370984948053,
            "unit": "iter/sec",
            "range": "stddev: 0.09571132821970382",
            "extra": "mean: 4.044428698799971 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.26695873187775004,
            "unit": "iter/sec",
            "range": "stddev: 0.08182409853997542",
            "extra": "mean: 3.7458973264000064 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "2f490ea94af261386f5fa1443994bc4721fbffb2",
          "message": "Merge pull request #1353 from procrastinate-org/fix-doc\n\nNew rule for migration naming",
          "timestamp": "2025-03-22T11:54:54+01:00",
          "tree_id": "62025c06ccfadeb55e4ab525517534dc763660fa",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/2f490ea94af261386f5fa1443994bc4721fbffb2"
        },
        "date": 1742641037285,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26487806748591874,
            "unit": "iter/sec",
            "range": "stddev: 0.1864761055206144",
            "extra": "mean: 3.775322016999996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4631974192146499,
            "unit": "iter/sec",
            "range": "stddev: 0.03354491151035513",
            "extra": "mean: 2.158906674599996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24963473367134303,
            "unit": "iter/sec",
            "range": "stddev: 0.06963681244043993",
            "extra": "mean: 4.005852812599994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2581905974406471,
            "unit": "iter/sec",
            "range": "stddev: 0.1476006198604388",
            "extra": "mean: 3.873107734799987 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bd0b15a7ec20974f230095e0197e11c20b6c41e8",
          "message": "Merge pull request #1355 from procrastinate-org/skip-before-version\n\nClean outdated skip-before-version",
          "timestamp": "2025-03-22T12:04:55+01:00",
          "tree_id": "0d0a12cbf2dd2a6560a1e9764f379b0e481673e7",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/bd0b15a7ec20974f230095e0197e11c20b6c41e8"
        },
        "date": 1742641641866,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26780092907496084,
            "unit": "iter/sec",
            "range": "stddev: 0.16294632967725062",
            "extra": "mean: 3.7341169930000033 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.49359052997628006,
            "unit": "iter/sec",
            "range": "stddev: 0.00923857957686554",
            "extra": "mean: 2.0259707981999897 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2537057690710642,
            "unit": "iter/sec",
            "range": "stddev: 0.05329002947182022",
            "extra": "mean: 3.9415737516000093 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.26870011737260124,
            "unit": "iter/sec",
            "range": "stddev: 0.08585224025189504",
            "extra": "mean: 3.7216210018000084 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kai.schlamp@gmail.com",
            "name": "Kai Schlamp",
            "username": "medihack"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "eff1c193fb1bbd8dd45d3902d772e1308027bbf6",
          "message": "Merge pull request #1344 from procrastinate-org/worker-heartbeat\n\nAdd heartbeats to detect stalled workers",
          "timestamp": "2025-03-22T16:47:41+01:00",
          "tree_id": "01757a6c49f1bb3595bf91668c6777f097242cc7",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/eff1c193fb1bbd8dd45d3902d772e1308027bbf6"
        },
        "date": 1742658613847,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2558994008799343,
            "unit": "iter/sec",
            "range": "stddev: 0.1323601043692533",
            "extra": "mean: 3.9077856241999998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.46298338455989246,
            "unit": "iter/sec",
            "range": "stddev: 0.024657182640093957",
            "extra": "mean: 2.159904725199999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24234901326018904,
            "unit": "iter/sec",
            "range": "stddev: 0.11257233158615047",
            "extra": "mean: 4.126280468599998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2507077499210117,
            "unit": "iter/sec",
            "range": "stddev: 0.10005132192450165",
            "extra": "mean: 3.9887079690000062 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d1ec4bb319e2e585ef4bac18c9e98b819a426e8f",
          "message": "Merge pull request #1357 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-03-24T04:40:25+01:00",
          "tree_id": "385ac541e5d23264b4afb98d57b3015859fb2b5b",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/d1ec4bb319e2e585ef4bac18c9e98b819a426e8f"
        },
        "date": 1742787766593,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27092564015532644,
            "unit": "iter/sec",
            "range": "stddev: 0.12457488730503116",
            "extra": "mean: 3.6910496896000042 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.50599585741758,
            "unit": "iter/sec",
            "range": "stddev: 0.02645194168912182",
            "extra": "mean: 1.9763007648000097 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2358710146487249,
            "unit": "iter/sec",
            "range": "stddev: 0.07371354186701094",
            "extra": "mean: 4.239605283799994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2750843811670013,
            "unit": "iter/sec",
            "range": "stddev: 0.08210730369651727",
            "extra": "mean: 3.6352481946000013 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "670460efe02ed20954d372e1c84da9bda4daa28b",
          "message": "Merge pull request #1359 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-03-29T02:01:49Z",
          "tree_id": "86a5b2475da1d9dc04f517490c1550a80cf6e887",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/670460efe02ed20954d372e1c84da9bda4daa28b"
        },
        "date": 1743213866718,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2534427945977694,
            "unit": "iter/sec",
            "range": "stddev: 0.2211945089939948",
            "extra": "mean: 3.9456635631999974 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.417649851657916,
            "unit": "iter/sec",
            "range": "stddev: 0.061631389469486174",
            "extra": "mean: 2.394350185999991 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22518448874260497,
            "unit": "iter/sec",
            "range": "stddev: 0.15422516940943107",
            "extra": "mean: 4.440803208 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2422593076714399,
            "unit": "iter/sec",
            "range": "stddev: 0.14473266910365293",
            "extra": "mean: 4.12780837859998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "085935f2083b1aa447d17e97402bcf05d9c2174d",
          "message": "Merge pull request #1360 from procrastinate-org/renovate/all\n\nUpdate pre-commit hook RobertCraigie/pyright-python to v1.1.398",
          "timestamp": "2025-03-29T02:07:17Z",
          "tree_id": "86a5b2475da1d9dc04f517490c1550a80cf6e887",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/085935f2083b1aa447d17e97402bcf05d9c2174d"
        },
        "date": 1743214180256,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26069795875939467,
            "unit": "iter/sec",
            "range": "stddev: 0.1812606049690227",
            "extra": "mean: 3.8358566547999997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4774373817579631,
            "unit": "iter/sec",
            "range": "stddev: 0.056005321568456216",
            "extra": "mean: 2.0945155076000104 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23140328479429473,
            "unit": "iter/sec",
            "range": "stddev: 0.0834435991863019",
            "extra": "mean: 4.32145983100001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.26125562232791183,
            "unit": "iter/sec",
            "range": "stddev: 0.10451368887507027",
            "extra": "mean: 3.8276688213999934 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "5bfe74f6186f705906361d9a369c79f838161980",
          "message": "Merge pull request #1362 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-03-31T02:34:36Z",
          "tree_id": "6aad9534347411e14437618890646d582f1f0924",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/5bfe74f6186f705906361d9a369c79f838161980"
        },
        "date": 1743388623201,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2579202069577491,
            "unit": "iter/sec",
            "range": "stddev: 0.10788738327926589",
            "extra": "mean: 3.8771681048000004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4153500198756757,
            "unit": "iter/sec",
            "range": "stddev: 0.0971470853758972",
            "extra": "mean: 2.407607926199989 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23572401240936353,
            "unit": "iter/sec",
            "range": "stddev: 0.12463918268323644",
            "extra": "mean: 4.242249186999999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.24939895124594533,
            "unit": "iter/sec",
            "range": "stddev: 0.21535406464221019",
            "extra": "mean: 4.009639956400008 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "574528736db87f7c13fdac10dcfe9f7c741e018b",
          "message": "Merge pull request #1366 from procrastinate-org/pre-commit-ci-update-config",
          "timestamp": "2025-04-09T16:04:17+02:00",
          "tree_id": "ae9991e1d876e6473aea7fd7a6e6528559549bd7",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/574528736db87f7c13fdac10dcfe9f7c741e018b"
        },
        "date": 1744207605027,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2559552318393429,
            "unit": "iter/sec",
            "range": "stddev: 0.15474100223266055",
            "extra": "mean: 3.9069332274000033 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.47408925427995235,
            "unit": "iter/sec",
            "range": "stddev: 0.023036182780314027",
            "extra": "mean: 2.109307458400005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24372999422773337,
            "unit": "iter/sec",
            "range": "stddev: 0.08648991914940396",
            "extra": "mean: 4.10290084799999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2610497224408406,
            "unit": "iter/sec",
            "range": "stddev: 0.058362110258795744",
            "extra": "mean: 3.830687849999998 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "dd51b6212228b65bc9060df7e8af8e098d50dd9a",
          "message": "Merge pull request #1364 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-04-09T14:07:02Z",
          "tree_id": "ffb21fa3fff74fd7b85d028e55697cf61642cd58",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/dd51b6212228b65bc9060df7e8af8e098d50dd9a"
        },
        "date": 1744207759556,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2798716167076122,
            "unit": "iter/sec",
            "range": "stddev: 0.15723490548225932",
            "extra": "mean: 3.573066864599997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5344383357560739,
            "unit": "iter/sec",
            "range": "stddev: 0.020116299252321355",
            "extra": "mean: 1.8711232579999943 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.25069487373208277,
            "unit": "iter/sec",
            "range": "stddev: 0.0917825929330114",
            "extra": "mean: 3.9889128370000035 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.28258919082527656,
            "unit": "iter/sec",
            "range": "stddev: 0.06341795878260284",
            "extra": "mean: 3.538705769599994 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "355f04980266628c45c54bedbc6f2733bc76daf5",
          "message": "Merge pull request #1369 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-04-12T02:34:20Z",
          "tree_id": "101f9f297f7e8b2cb9835374734b188986a4bed8",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/355f04980266628c45c54bedbc6f2733bc76daf5"
        },
        "date": 1744425396431,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27929428036529924,
            "unit": "iter/sec",
            "range": "stddev: 0.13804032622415163",
            "extra": "mean: 3.580452842400007 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5241714076658304,
            "unit": "iter/sec",
            "range": "stddev: 0.02981750242411373",
            "extra": "mean: 1.9077728876000037 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2622644488742271,
            "unit": "iter/sec",
            "range": "stddev: 0.05888714182807802",
            "extra": "mean: 3.8129453087999936 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.28051824021150534,
            "unit": "iter/sec",
            "range": "stddev: 0.047795795051412245",
            "extra": "mean: 3.564830576600008 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3e10ca3f2c5310c5164b6e6129b76309fdc185d9",
          "message": "Merge pull request #1370 from procrastinate-org/renovate/all\n\nUpdate pre-commit hook RobertCraigie/pyright-python to v1.1.399",
          "timestamp": "2025-04-12T02:39:39Z",
          "tree_id": "101f9f297f7e8b2cb9835374734b188986a4bed8",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/3e10ca3f2c5310c5164b6e6129b76309fdc185d9"
        },
        "date": 1744425726608,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27146355105369235,
            "unit": "iter/sec",
            "range": "stddev: 0.12461058195963624",
            "extra": "mean: 3.6837357947999863 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4722647061057065,
            "unit": "iter/sec",
            "range": "stddev: 0.03657668862829765",
            "extra": "mean: 2.1174565599999995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.25488548093064906,
            "unit": "iter/sec",
            "range": "stddev: 0.06884757374659393",
            "extra": "mean: 3.9233305731999963 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2672957632404307,
            "unit": "iter/sec",
            "range": "stddev: 0.12821914590071715",
            "extra": "mean: 3.741174150600011 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "d6d1fcadbfcef8e76919b9b222748f2927f3ea53",
          "message": "Merge pull request #1372 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-04-19T01:28:56Z",
          "tree_id": "95cd8dad8297ad5b27d38db361bfe02ca755b76c",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/d6d1fcadbfcef8e76919b9b222748f2927f3ea53"
        },
        "date": 1745026278928,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2614456358591323,
            "unit": "iter/sec",
            "range": "stddev: 0.17212525182516963",
            "extra": "mean: 3.824886947200002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4848132179953595,
            "unit": "iter/sec",
            "range": "stddev: 0.031092403922060308",
            "extra": "mean: 2.062650032799996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24743774793659143,
            "unit": "iter/sec",
            "range": "stddev: 0.07223963727959123",
            "extra": "mean: 4.041420552600004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.259847873354508,
            "unit": "iter/sec",
            "range": "stddev: 0.10032785920144316",
            "extra": "mean: 3.848405557800004 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kai.schlamp@gmail.com",
            "name": "Kai Schlamp",
            "username": "medihack"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "072da20ff679b1860ae0fbb3bca6547340d0a65a",
          "message": "Merge pull request #1377 from procrastinate-org/fix-sync-pre-commit\n\nFix sync-pre-commit",
          "timestamp": "2025-05-02T18:59:59+02:00",
          "tree_id": "d7a35b57b5ee0084744ac4ec1173d925878557e7",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/072da20ff679b1860ae0fbb3bca6547340d0a65a"
        },
        "date": 1746205345765,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.25079257770173274,
            "unit": "iter/sec",
            "range": "stddev: 0.20940987602459984",
            "extra": "mean: 3.987358833199994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4598904145361265,
            "unit": "iter/sec",
            "range": "stddev: 0.09943623663496895",
            "extra": "mean: 2.174431056599997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24530234259050876,
            "unit": "iter/sec",
            "range": "stddev: 0.13049968711867682",
            "extra": "mean: 4.076601916800007 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2567770168964415,
            "unit": "iter/sec",
            "range": "stddev: 0.11956254939828312",
            "extra": "mean: 3.8944295407999903 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3fcc4e3231fa3b6bd01e2596fca6f39400ed8519",
          "message": "Merge pull request #1373 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-05-02T17:04:43Z",
          "tree_id": "85affe611216725dc737adebf2fab318def6e18a",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/3fcc4e3231fa3b6bd01e2596fca6f39400ed8519"
        },
        "date": 1746205637801,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2491076095045563,
            "unit": "iter/sec",
            "range": "stddev: 0.1618606568785504",
            "extra": "mean: 4.014329397599994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.43884267245906156,
            "unit": "iter/sec",
            "range": "stddev: 0.047677772615233795",
            "extra": "mean: 2.278720969400001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22644144147297213,
            "unit": "iter/sec",
            "range": "stddev: 0.15408073084490245",
            "extra": "mean: 4.416152774399995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.24957320595861282,
            "unit": "iter/sec",
            "range": "stddev: 0.0767596924357842",
            "extra": "mean: 4.006840382399991 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "916ba8d1734fb0c39aa3da9b3eb096dd1745935c",
          "message": "Merge pull request #1374 from procrastinate-org/renovate/major-all\n\nUpdate astral-sh/setup-uv action to v6",
          "timestamp": "2025-05-02T19:06:23+02:00",
          "tree_id": "fd89b4fa09ea66cd18e30fbbdffbffa5cc6dbfc0",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/916ba8d1734fb0c39aa3da9b3eb096dd1745935c"
        },
        "date": 1746205736002,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.24107365667662006,
            "unit": "iter/sec",
            "range": "stddev: 0.10862188247671724",
            "extra": "mean: 4.148109809199997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.40478916786557134,
            "unit": "iter/sec",
            "range": "stddev: 0.07742767448761118",
            "extra": "mean: 2.4704218378000062 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22198784965070734,
            "unit": "iter/sec",
            "range": "stddev: 0.21247432208689127",
            "extra": "mean: 4.504751055399998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.24094488851874607,
            "unit": "iter/sec",
            "range": "stddev: 0.10320615724969305",
            "extra": "mean: 4.150326683199995 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "7f82ec4da989e35d2e168334e76ce1c38b0dd4b7",
          "message": "Merge pull request #1379 from procrastinate-org/renovate/all\n\nUpdate pre-commit hook RobertCraigie/pyright-python to v1.1.400",
          "timestamp": "2025-05-03T02:33:08Z",
          "tree_id": "fd89b4fa09ea66cd18e30fbbdffbffa5cc6dbfc0",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/7f82ec4da989e35d2e168334e76ce1c38b0dd4b7"
        },
        "date": 1746239735962,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26608138801441233,
            "unit": "iter/sec",
            "range": "stddev: 0.11963729306528881",
            "extra": "mean: 3.7582485849999956 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.484102851727383,
            "unit": "iter/sec",
            "range": "stddev: 0.02537736456200896",
            "extra": "mean: 2.0656767387999992 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2502050634912848,
            "unit": "iter/sec",
            "range": "stddev: 0.07884400133816946",
            "extra": "mean: 3.9967216731999997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.260652729838817,
            "unit": "iter/sec",
            "range": "stddev: 0.19392646396050645",
            "extra": "mean: 3.8365222594000157 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "4231a19b96a57fdac02d2f140d6f88bae334726a",
          "message": "Merge pull request #1365 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-05-04T14:13:00+02:00",
          "tree_id": "a1be351ec8edcebe69e42eac5e3eb8ede52e40bf",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/4231a19b96a57fdac02d2f140d6f88bae334726a"
        },
        "date": 1746360928980,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.253993330486262,
            "unit": "iter/sec",
            "range": "stddev: 0.14955079682481628",
            "extra": "mean: 3.937111254399997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.47419698665238647,
            "unit": "iter/sec",
            "range": "stddev: 0.010786919156826946",
            "extra": "mean: 2.10882824680001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2211383073246403,
            "unit": "iter/sec",
            "range": "stddev: 0.14747880650685455",
            "extra": "mean: 4.522056861600004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2384713645908347,
            "unit": "iter/sec",
            "range": "stddev: 0.10684497339843099",
            "extra": "mean: 4.193375593400003 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "3597485f202921e89797ef424eddeeb5ff707af2",
          "message": "Merge pull request #1383 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-05-04T12:21:35Z",
          "tree_id": "a11d604d69024f453706fa40f837a8a70272df6e",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/3597485f202921e89797ef424eddeeb5ff707af2"
        },
        "date": 1746361446014,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2562753740285217,
            "unit": "iter/sec",
            "range": "stddev: 0.11652375795890757",
            "extra": "mean: 3.9020526407999965 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.46575365072287267,
            "unit": "iter/sec",
            "range": "stddev: 0.03933561080265417",
            "extra": "mean: 2.1470577813999965 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24196558975650587,
            "unit": "iter/sec",
            "range": "stddev: 0.051083258514661126",
            "extra": "mean: 4.132819054999999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.24959477377456774,
            "unit": "iter/sec",
            "range": "stddev: 0.13294885297831013",
            "extra": "mean: 4.006494146 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "cd852adf9456b3f43b2477b64900cb69f2e64751",
          "message": "Merge pull request #1384 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-05-05T03:37:27Z",
          "tree_id": "50d2df430ac72c9986d7f042c98535e2d58def24",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/cd852adf9456b3f43b2477b64900cb69f2e64751"
        },
        "date": 1746416406160,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2403034448782903,
            "unit": "iter/sec",
            "range": "stddev: 0.07512474397767237",
            "extra": "mean: 4.16140517880001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.39688895071607316,
            "unit": "iter/sec",
            "range": "stddev: 0.09062063793726272",
            "extra": "mean: 2.519596472000001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.21575234700943594,
            "unit": "iter/sec",
            "range": "stddev: 0.16175827561370434",
            "extra": "mean: 4.634943785600001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.24242931893531985,
            "unit": "iter/sec",
            "range": "stddev: 0.129396878879713",
            "extra": "mean: 4.12491362180001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kai.schlamp@gmail.com",
            "name": "Kai Schlamp",
            "username": "medihack"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "daedad09923b7e32542908356c2c29292f62f4bc",
          "message": "Merge pull request #1378 from procrastinate-org/add_django_worker_model\n\nAdd a Django model for the worker",
          "timestamp": "2025-05-05T08:58:43+02:00",
          "tree_id": "817c9f76cc8c436e3dbe08212f10d54351375c20",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/daedad09923b7e32542908356c2c29292f62f4bc"
        },
        "date": 1746428464825,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2697680626808448,
            "unit": "iter/sec",
            "range": "stddev: 0.11362032706051893",
            "extra": "mean: 3.7068880209999975 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5080094992574335,
            "unit": "iter/sec",
            "range": "stddev: 0.02478227367660229",
            "extra": "mean: 1.9684671280000032 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24709895492009987,
            "unit": "iter/sec",
            "range": "stddev: 0.023173983628475885",
            "extra": "mean: 4.046961673000004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2725330945227133,
            "unit": "iter/sec",
            "range": "stddev: 0.050109296958396",
            "extra": "mean: 3.6692791448000035 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "9664150fce1a533818803799a4f7423b5755b413",
          "message": "Merge pull request #1371 from philherbert/patch-1",
          "timestamp": "2025-05-05T16:31:59+02:00",
          "tree_id": "e11cdaeaf8d60158588c32c6e997a86a43e5682a",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/9664150fce1a533818803799a4f7423b5755b413"
        },
        "date": 1746455673361,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.25090660841301304,
            "unit": "iter/sec",
            "range": "stddev: 0.05729365722044364",
            "extra": "mean: 3.9855466793999996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.46166657547628515,
            "unit": "iter/sec",
            "range": "stddev: 0.05417724368534785",
            "extra": "mean: 2.1660654097999954 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23648992848074904,
            "unit": "iter/sec",
            "range": "stddev: 0.04325023672961858",
            "extra": "mean: 4.2285098837999895 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2505211864934943,
            "unit": "iter/sec",
            "range": "stddev: 0.10180801352254362",
            "extra": "mean: 3.9916783645999887 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kai.schlamp@gmail.com",
            "name": "Kai Schlamp",
            "username": "medihack"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c85e74a6e0f709f828996dd5b166ba0c1bd4988b",
          "message": "Merge pull request #1382 from procrastinate-org/batch-defer\n\nAllow to batch defer multiple jobs at once",
          "timestamp": "2025-05-09T20:51:15+02:00",
          "tree_id": "efc0a0411415678c3d550c609c6753a724f2e9b5",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/c85e74a6e0f709f828996dd5b166ba0c1bd4988b"
        },
        "date": 1746816903975,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.25376864462454274,
            "unit": "iter/sec",
            "range": "stddev: 0.12634205800152778",
            "extra": "mean: 3.9405971588 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.463316336348979,
            "unit": "iter/sec",
            "range": "stddev: 0.01900497241122303",
            "extra": "mean: 2.1583525586000065 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3482805019619729,
            "unit": "iter/sec",
            "range": "stddev: 0.2247290360398696",
            "extra": "mean: 2.8712488766000037 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5689938406717157,
            "unit": "iter/sec",
            "range": "stddev: 0.2293563910951611",
            "extra": "mean: 1.757488268800006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23498893846368946,
            "unit": "iter/sec",
            "range": "stddev: 0.1256311364940607",
            "extra": "mean: 4.255519457800011 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2513730703966135,
            "unit": "iter/sec",
            "range": "stddev: 0.18916718549804193",
            "extra": "mean: 3.9781508752000034 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32087593863748637,
            "unit": "iter/sec",
            "range": "stddev: 0.07699797078066975",
            "extra": "mean: 3.116469262999999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.30991571462432244,
            "unit": "iter/sec",
            "range": "stddev: 0.1346808230536127",
            "extra": "mean: 3.2266837491999807 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kai.schlamp@gmail.com",
            "name": "Kai Schlamp",
            "username": "medihack"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "14d16521a9e3f647915cae2c6ab34192ce975b03",
          "message": "Merge pull request #1386 from procrastinate-org/discussions_benchmarks\n\nAdd a section about benchmarks to the discussions",
          "timestamp": "2025-05-09T21:10:55+02:00",
          "tree_id": "d11128383d5a476f3770d3e16b44bf6d76e61e1f",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/14d16521a9e3f647915cae2c6ab34192ce975b03"
        },
        "date": 1746818072858,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2633868364111495,
            "unit": "iter/sec",
            "range": "stddev: 0.11815896438249592",
            "extra": "mean: 3.796696955799985 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.48828068399495256,
            "unit": "iter/sec",
            "range": "stddev: 0.038366372070551574",
            "extra": "mean: 2.0480023739999864 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3600060512265123,
            "unit": "iter/sec",
            "range": "stddev: 0.19269793881496494",
            "extra": "mean: 2.7777310870000065 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5910489593247016,
            "unit": "iter/sec",
            "range": "stddev: 0.19658202586271709",
            "extra": "mean: 1.69190721719998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2442784365526221,
            "unit": "iter/sec",
            "range": "stddev: 0.0791137909646621",
            "extra": "mean: 4.093689210200023 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2646135179616088,
            "unit": "iter/sec",
            "range": "stddev: 0.06865313287322022",
            "extra": "mean: 3.7790964259999895 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3129287954541339,
            "unit": "iter/sec",
            "range": "stddev: 0.14416850755737015",
            "extra": "mean: 3.1956151512000135 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3307762418393517,
            "unit": "iter/sec",
            "range": "stddev: 0.04472642971329383",
            "extra": "mean: 3.0231917335999925 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "c9a1c69175c35ea4a2393f5858061045d56d028c",
          "message": "Merge pull request #1387 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-05-10T03:12:04Z",
          "tree_id": "84010456c91f5af18c799c4830de299ee8e19ed6",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/c9a1c69175c35ea4a2393f5858061045d56d028c"
        },
        "date": 1746846959454,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2540539187301056,
            "unit": "iter/sec",
            "range": "stddev: 0.11744775251493315",
            "extra": "mean: 3.936172309400001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.44841678917386707,
            "unit": "iter/sec",
            "range": "stddev: 0.02714121523885314",
            "extra": "mean: 2.230068151199987 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3443415787742265,
            "unit": "iter/sec",
            "range": "stddev: 0.23770529482568575",
            "extra": "mean: 2.9040930914 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.548554327839759,
            "unit": "iter/sec",
            "range": "stddev: 0.20888236781179173",
            "extra": "mean: 1.8229734946000007 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22690316705229754,
            "unit": "iter/sec",
            "range": "stddev: 0.14584360092154813",
            "extra": "mean: 4.407166338800005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.23951893096770982,
            "unit": "iter/sec",
            "range": "stddev: 0.1568456936217904",
            "extra": "mean: 4.175035334200004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3079855761255579,
            "unit": "iter/sec",
            "range": "stddev: 0.10153889346044288",
            "extra": "mean: 3.2469053017999956 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3004603763133273,
            "unit": "iter/sec",
            "range": "stddev: 0.07889703145426961",
            "extra": "mean: 3.328225878799992 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f5dc1f555826652ce4c6fb1f7f163cf4a9430efe",
          "message": "Merge pull request #1388 from procrastinate-org/fix-json",
          "timestamp": "2025-05-10T15:42:32+02:00",
          "tree_id": "73fc57eb5ea2e1bdc2eb72cae4ffe6720acf65ae",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/f5dc1f555826652ce4c6fb1f7f163cf4a9430efe"
        },
        "date": 1746884770626,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26285584103039533,
            "unit": "iter/sec",
            "range": "stddev: 0.08655295765297594",
            "extra": "mean: 3.8043666675999988 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.49574544639700424,
            "unit": "iter/sec",
            "range": "stddev: 0.021223939442104434",
            "extra": "mean: 2.0171642669999983 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3255033915223041,
            "unit": "iter/sec",
            "range": "stddev: 0.10733074426735707",
            "extra": "mean: 3.072164610400006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.584535346226406,
            "unit": "iter/sec",
            "range": "stddev: 0.23089456624691357",
            "extra": "mean: 1.7107605322000041 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24370329995181966,
            "unit": "iter/sec",
            "range": "stddev: 0.18928253958765553",
            "extra": "mean: 4.103350263199968 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2641251159765788,
            "unit": "iter/sec",
            "range": "stddev: 0.08466770552079948",
            "extra": "mean: 3.7860844710000037 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3106792594620619,
            "unit": "iter/sec",
            "range": "stddev: 0.08428712457911304",
            "extra": "mean: 3.2187536488000204 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3234116794101288,
            "unit": "iter/sec",
            "range": "stddev: 0.14373118045154987",
            "extra": "mean: 3.092034282200018 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "f23aa5b6aed3e4041c14a5f625e8efd2f5d7a455",
          "message": "Merge pull request #1389 from procrastinate-org/remove-success-job",
          "timestamp": "2025-05-10T15:48:55+02:00",
          "tree_id": "59fedb5bfb1544b2a5ecac22cfcd55bb9d87757c",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/f23aa5b6aed3e4041c14a5f625e8efd2f5d7a455"
        },
        "date": 1746885160015,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.25515899697802685,
            "unit": "iter/sec",
            "range": "stddev: 0.13653135270625374",
            "extra": "mean: 3.9191249842000104 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4473615699056135,
            "unit": "iter/sec",
            "range": "stddev: 0.035153453998573496",
            "extra": "mean: 2.2353283502000068 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3767203225865879,
            "unit": "iter/sec",
            "range": "stddev: 0.031560128743233766",
            "extra": "mean: 2.654489126400006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5531975053963435,
            "unit": "iter/sec",
            "range": "stddev: 0.2117150662615327",
            "extra": "mean: 1.807672649 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22367628426640357,
            "unit": "iter/sec",
            "range": "stddev: 0.500787001275422",
            "extra": "mean: 4.470746656400001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.24782483275663478,
            "unit": "iter/sec",
            "range": "stddev: 0.16048338713951124",
            "extra": "mean: 4.0351081401999975 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.31960957065543566,
            "unit": "iter/sec",
            "range": "stddev: 0.062410284004140344",
            "extra": "mean: 3.1288174442000014 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.31122347974552206,
            "unit": "iter/sec",
            "range": "stddev: 0.12347156145167616",
            "extra": "mean: 3.2131251819999873 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "463deadc7d295199b0ae668eab546b0859370161",
          "message": "Merge pull request #1390 from procrastinate-org/sync-pre-commit",
          "timestamp": "2025-05-10T15:51:13+02:00",
          "tree_id": "70ac18364711208cdba3925fd740aea4cd43f755",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/463deadc7d295199b0ae668eab546b0859370161"
        },
        "date": 1746885293668,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26005104370303195,
            "unit": "iter/sec",
            "range": "stddev: 0.13825995867095853",
            "extra": "mean: 3.8453989099999943 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.47212098805705527,
            "unit": "iter/sec",
            "range": "stddev: 0.030123927334710966",
            "extra": "mean: 2.1181011335999984 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.36636895596380614,
            "unit": "iter/sec",
            "range": "stddev: 0.09878906542600317",
            "extra": "mean: 2.729488903800001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5698965992284847,
            "unit": "iter/sec",
            "range": "stddev: 0.20274948740172946",
            "extra": "mean: 1.754704276800004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23849192661153495,
            "unit": "iter/sec",
            "range": "stddev: 0.12908703965035126",
            "extra": "mean: 4.193014053799982 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.25828802074531443,
            "unit": "iter/sec",
            "range": "stddev: 0.07738642667000734",
            "extra": "mean: 3.8716468426000006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3117102396179251,
            "unit": "iter/sec",
            "range": "stddev: 0.053922982908727",
            "extra": "mean: 3.208107636200009 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.31648869231204635,
            "unit": "iter/sec",
            "range": "stddev: 0.14966148052464476",
            "extra": "mean: 3.1596705483999927 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "ewjoachim@gmail.com",
            "name": "Joachim Jablon",
            "username": "ewjoachim"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "88b8878ca9078a971270557f43eb29d15527cd98",
          "message": "Merge pull request #1391 from procrastinate-org/fix-badges",
          "timestamp": "2025-05-12T00:54:22+02:00",
          "tree_id": "711e877ffbcbd4c64c3f5366b42c20dabf6034eb",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/88b8878ca9078a971270557f43eb29d15527cd98"
        },
        "date": 1747004287892,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.21991229439666124,
            "unit": "iter/sec",
            "range": "stddev: 1.367152386872372",
            "extra": "mean: 4.547267367400002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4450510581355062,
            "unit": "iter/sec",
            "range": "stddev: 0.015260564994129356",
            "extra": "mean: 2.2469332039999927 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3684138325736291,
            "unit": "iter/sec",
            "range": "stddev: 0.024773236595518784",
            "extra": "mean: 2.714338908000002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5351589609697973,
            "unit": "iter/sec",
            "range": "stddev: 0.22189014456837672",
            "extra": "mean: 1.868603672800009 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23231668656780258,
            "unit": "iter/sec",
            "range": "stddev: 0.11124972530568478",
            "extra": "mean: 4.304469105399994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2466964006016157,
            "unit": "iter/sec",
            "range": "stddev: 0.1269965805131304",
            "extra": "mean: 4.053565425200008 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.31079934987730456,
            "unit": "iter/sec",
            "range": "stddev: 0.08488582557357316",
            "extra": "mean: 3.217509947799999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.30162985528215225,
            "unit": "iter/sec",
            "range": "stddev: 0.13822822385694947",
            "extra": "mean: 3.315321684799983 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "29139614+renovate[bot]@users.noreply.github.com",
            "name": "renovate[bot]",
            "username": "renovate[bot]"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "bb75a56b4dad2da8538a39ae9b8d2f10941e5a9c",
          "message": "Merge pull request #1392 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-05-12T02:48:16Z",
          "tree_id": "0d25e4a7f272618baf8ec9b54e3079e8c045b8ae",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/bb75a56b4dad2da8538a39ae9b8d2f10941e5a9c"
        },
        "date": 1747018328261,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.24697020879614615,
            "unit": "iter/sec",
            "range": "stddev: 0.1331932478438396",
            "extra": "mean: 4.0490713631999995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.41378740445994033,
            "unit": "iter/sec",
            "range": "stddev: 0.059685453169176124",
            "extra": "mean: 2.416699950800006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3287435384300346,
            "unit": "iter/sec",
            "range": "stddev: 0.21568352506550964",
            "extra": "mean: 3.041884883199998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5475519923422254,
            "unit": "iter/sec",
            "range": "stddev: 0.2965138063207665",
            "extra": "mean: 1.8263105860000053 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.21934367248709508,
            "unit": "iter/sec",
            "range": "stddev: 0.19003842898020462",
            "extra": "mean: 4.5590556074 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.23514800797307456,
            "unit": "iter/sec",
            "range": "stddev: 0.16089461854392323",
            "extra": "mean: 4.252640745799999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.29655973295194954,
            "unit": "iter/sec",
            "range": "stddev: 0.20999620662376317",
            "extra": "mean: 3.372001957400016 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.309307944429952,
            "unit": "iter/sec",
            "range": "stddev: 0.07508327806251257",
            "extra": "mean: 3.233023974999992 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "kai.schlamp@gmail.com",
            "name": "Kai Schlamp",
            "username": "medihack"
          },
          "committer": {
            "email": "noreply@github.com",
            "name": "GitHub",
            "username": "web-flow"
          },
          "distinct": true,
          "id": "735d2bb8bfc5be3c42f4771523fa06ed88dff454",
          "message": "Merge pull request #1393 from procrastinate-org/fix-publish-workflow\n\nFix publish workflow by using ref",
          "timestamp": "2025-05-14T21:14:05+02:00",
          "tree_id": "1a92b30e5fe3452d2444b1232a26ade199d2c6dd",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/735d2bb8bfc5be3c42f4771523fa06ed88dff454"
        },
        "date": 1747250263096,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26592167916864645,
            "unit": "iter/sec",
            "range": "stddev: 0.06462425962562186",
            "extra": "mean: 3.760505736600001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4879190617720525,
            "unit": "iter/sec",
            "range": "stddev: 0.01614906573043973",
            "extra": "mean: 2.0495202551999965 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.360842871984857,
            "unit": "iter/sec",
            "range": "stddev: 0.19203500137154134",
            "extra": "mean: 2.771289327400004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5866337105171644,
            "unit": "iter/sec",
            "range": "stddev: 0.221729647912213",
            "extra": "mean: 1.7046412132000057 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23454243418909632,
            "unit": "iter/sec",
            "range": "stddev: 0.21216363198196592",
            "extra": "mean: 4.263620796199996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2636957972179979,
            "unit": "iter/sec",
            "range": "stddev: 0.08811307752493612",
            "extra": "mean: 3.7922485323999977 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3120540723511981,
            "unit": "iter/sec",
            "range": "stddev: 0.09224391308990836",
            "extra": "mean: 3.2045728243999974 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.324420916173353,
            "unit": "iter/sec",
            "range": "stddev: 0.16865904353670702",
            "extra": "mean: 3.082415313399997 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}