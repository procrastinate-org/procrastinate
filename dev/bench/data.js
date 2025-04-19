window.BENCHMARK_DATA = {
  "lastUpdate": 1745026279237,
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
      }
    ]
  }
}