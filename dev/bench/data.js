window.BENCHMARK_DATA = {
  "lastUpdate": 1758933869868,
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
          "id": "c49a2a6ff1951fafd4faf57167110f5f4ce39108",
          "message": "Merge pull request #1394 from procrastinate-org/merge-queue",
          "timestamp": "2025-05-14T22:52:32+02:00",
          "tree_id": "140dbf54f3845adfc9435027e4f280b07eea6454",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/c49a2a6ff1951fafd4faf57167110f5f4ce39108"
        },
        "date": 1747256207445,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.23554218654346848,
            "unit": "iter/sec",
            "range": "stddev: 0.0682503367705353",
            "extra": "mean: 4.245523974599996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.42365167674944704,
            "unit": "iter/sec",
            "range": "stddev: 0.03971572627891516",
            "extra": "mean: 2.3604296993999925 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.32252563718619004,
            "unit": "iter/sec",
            "range": "stddev: 0.211638185006909",
            "extra": "mean: 3.1005287167999995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5097372155535311,
            "unit": "iter/sec",
            "range": "stddev: 0.2334281201071257",
            "extra": "mean: 1.9617951553999944 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.19965954209019926,
            "unit": "iter/sec",
            "range": "stddev: 0.3025912815971767",
            "extra": "mean: 5.0085259614000055 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.22351124574884193,
            "unit": "iter/sec",
            "range": "stddev: 0.32063083738921405",
            "extra": "mean: 4.474047811999998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.27107145357141976,
            "unit": "iter/sec",
            "range": "stddev: 0.15169614772827267",
            "extra": "mean: 3.689064218399994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.28181131750473504,
            "unit": "iter/sec",
            "range": "stddev: 0.19349643088222904",
            "extra": "mean: 3.5484735278000246 sec\nrounds: 5"
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
          "id": "c2e86a8a2da789f17fd04ee5e2f7528ac7108adb",
          "message": "Merge pull request #1395 from procrastinate-org/remove-duplicate-benchmark-action\n\nRemove duplicate GitHub Action benchmark workflow",
          "timestamp": "2025-05-14T20:59:50Z",
          "tree_id": "baf516a7a4e8d957bb69fce432fc5bf5001ab750",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/c2e86a8a2da789f17fd04ee5e2f7528ac7108adb"
        },
        "date": 1747257460690,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2502166655507463,
            "unit": "iter/sec",
            "range": "stddev: 0.08035748983043488",
            "extra": "mean: 3.996536352999999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.44999015466990566,
            "unit": "iter/sec",
            "range": "stddev: 0.05690674693689471",
            "extra": "mean: 2.2222708422000013 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.35402738833436515,
            "unit": "iter/sec",
            "range": "stddev: 0.06155028148385945",
            "extra": "mean: 2.824640219799997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5500616598548405,
            "unit": "iter/sec",
            "range": "stddev: 0.19096224952938265",
            "extra": "mean: 1.8179780067999958 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22726002938716516,
            "unit": "iter/sec",
            "range": "stddev: 0.11928988543478596",
            "extra": "mean: 4.400245844800002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2368789033909473,
            "unit": "iter/sec",
            "range": "stddev: 0.2358356250769804",
            "extra": "mean: 4.221566318000003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3046456574568377,
            "unit": "iter/sec",
            "range": "stddev: 0.17543177315095457",
            "extra": "mean: 3.2825020660000064 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.2913868503825995,
            "unit": "iter/sec",
            "range": "stddev: 0.22345024331015678",
            "extra": "mean: 3.431863856199999 sec\nrounds: 5"
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
          "id": "d5a4e02045b0f0c7e6e9a618b8539c5751a8ac4e",
          "message": "Merge pull request #1399 from jakajancar/patch-1\n\nRemove rogue debug print()",
          "timestamp": "2025-05-16T08:04:10+02:00",
          "tree_id": "cbc3b4b7610d70e7e26e389e31703071cc45f8c9",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/d5a4e02045b0f0c7e6e9a618b8539c5751a8ac4e"
        },
        "date": 1747375663379,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27580286509966956,
            "unit": "iter/sec",
            "range": "stddev: 0.08742987858935089",
            "extra": "mean: 3.625778142800004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5220656306433674,
            "unit": "iter/sec",
            "range": "stddev: 0.014683386145358666",
            "extra": "mean: 1.9154679819999842 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.35241309556321687,
            "unit": "iter/sec",
            "range": "stddev: 0.12993129243318488",
            "extra": "mean: 2.83757900199999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6264832467777833,
            "unit": "iter/sec",
            "range": "stddev: 0.2029438434095412",
            "extra": "mean: 1.5962118782000005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.25857783584022426,
            "unit": "iter/sec",
            "range": "stddev: 0.05101149469949758",
            "extra": "mean: 3.8673074849999978 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2754336157237761,
            "unit": "iter/sec",
            "range": "stddev: 0.07944395726033383",
            "extra": "mean: 3.630638901399999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.33047420693670015,
            "unit": "iter/sec",
            "range": "stddev: 0.16431099482917866",
            "extra": "mean: 3.0259547614000097 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3277885125478143,
            "unit": "iter/sec",
            "range": "stddev: 0.1167490823903784",
            "extra": "mean: 3.050747545199988 sec\nrounds: 5"
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
          "id": "075ff87f15212f9b9d93e3937199026eddc129fe",
          "message": "Merge pull request #1400 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-05-17T01:42:28Z",
          "tree_id": "9b90eda5170fa1d4feffdf20872cd88eae213f7f",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/075ff87f15212f9b9d93e3937199026eddc129fe"
        },
        "date": 1747446373841,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2547754251946026,
            "unit": "iter/sec",
            "range": "stddev: 0.1912304469021445",
            "extra": "mean: 3.9250253404000004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.49441230612560283,
            "unit": "iter/sec",
            "range": "stddev: 0.03453982142267305",
            "extra": "mean: 2.022603376999996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3896982708419626,
            "unit": "iter/sec",
            "range": "stddev: 0.018418455065327657",
            "extra": "mean: 2.5660878551999984 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5868077113550547,
            "unit": "iter/sec",
            "range": "stddev: 0.22481784987784548",
            "extra": "mean: 1.704135751200002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24773194102377746,
            "unit": "iter/sec",
            "range": "stddev: 0.07845750235096118",
            "extra": "mean: 4.036621179600007 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2504554784583522,
            "unit": "iter/sec",
            "range": "stddev: 0.12849863329042802",
            "extra": "mean: 3.9927255979999985 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.311980279656639,
            "unit": "iter/sec",
            "range": "stddev: 0.09915434134761013",
            "extra": "mean: 3.2053308020000033 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.30504788242198094,
            "unit": "iter/sec",
            "range": "stddev: 0.2222365063981879",
            "extra": "mean: 3.278173878999996 sec\nrounds: 5"
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
          "id": "3a63e3a2413e433f23eb934bd1a4f4e079957029",
          "message": "Merge pull request #1401 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-05-24T03:32:29Z",
          "tree_id": "e124315bfbf4916e57fe4ffdd6afe25f2e24196c",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/3a63e3a2413e433f23eb934bd1a4f4e079957029"
        },
        "date": 1748057766021,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2771813011724707,
            "unit": "iter/sec",
            "range": "stddev: 0.06435612859491158",
            "extra": "mean: 3.6077469719999953 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5136587980784864,
            "unit": "iter/sec",
            "range": "stddev: 0.012628400906306615",
            "extra": "mean: 1.946817622399999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.38537595899144467,
            "unit": "iter/sec",
            "range": "stddev: 0.17107382160285645",
            "extra": "mean: 2.594868664400002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.634846587543276,
            "unit": "iter/sec",
            "range": "stddev: 0.17472925685047336",
            "extra": "mean: 1.57518370520001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24339192240128985,
            "unit": "iter/sec",
            "range": "stddev: 0.10785107368209501",
            "extra": "mean: 4.108599784800009 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2748211604472572,
            "unit": "iter/sec",
            "range": "stddev: 0.09555759692867695",
            "extra": "mean: 3.638729995800003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3284221383440022,
            "unit": "iter/sec",
            "range": "stddev: 0.13309469630433254",
            "extra": "mean: 3.044861729000013 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3056173530907137,
            "unit": "iter/sec",
            "range": "stddev: 0.22499446709794443",
            "extra": "mean: 3.2720655090000035 sec\nrounds: 5"
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
          "id": "a2937e19a29e4982787391a5a013e3eb8585d618",
          "message": "Merge pull request #1402 from procrastinate-org/renovate/all\n\nUpdate pre-commit hook RobertCraigie/pyright-python to v1.1.401",
          "timestamp": "2025-05-24T03:41:18Z",
          "tree_id": "e124315bfbf4916e57fe4ffdd6afe25f2e24196c",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/a2937e19a29e4982787391a5a013e3eb8585d618"
        },
        "date": 1748058301477,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2606088145908143,
            "unit": "iter/sec",
            "range": "stddev: 0.0768488647181584",
            "extra": "mean: 3.8371687526000016 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4592437146364917,
            "unit": "iter/sec",
            "range": "stddev: 0.03458908723756696",
            "extra": "mean: 2.1774930567999973 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.36367485204685635,
            "unit": "iter/sec",
            "range": "stddev: 0.16552924884317663",
            "extra": "mean: 2.7497089622000006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5588036934814559,
            "unit": "iter/sec",
            "range": "stddev: 0.24702694084822704",
            "extra": "mean: 1.789537205399995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24016491128830483,
            "unit": "iter/sec",
            "range": "stddev: 0.09728334128255389",
            "extra": "mean: 4.163805589400004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2575941607052128,
            "unit": "iter/sec",
            "range": "stddev: 0.1426867622776565",
            "extra": "mean: 3.882075576799997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.31094200382915427,
            "unit": "iter/sec",
            "range": "stddev: 0.06464397496714773",
            "extra": "mean: 3.2160338188000024 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.30967424634700064,
            "unit": "iter/sec",
            "range": "stddev: 0.17065197736927162",
            "extra": "mean: 3.2291997535999997 sec\nrounds: 5"
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
          "id": "3a18867df9393dd5b9123b1408a67399aa6c94f7",
          "message": "Merge pull request #1404 from procrastinate-org/sync-pre-commit-with-uv",
          "timestamp": "2025-05-28T00:00:36+02:00",
          "tree_id": "adf31784d00a1d622f3b09d5bc666103a09954a8",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/3a18867df9393dd5b9123b1408a67399aa6c94f7"
        },
        "date": 1748383453592,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26229569153896076,
            "unit": "iter/sec",
            "range": "stddev: 0.15136106457315035",
            "extra": "mean: 3.812491139799994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5001701819040527,
            "unit": "iter/sec",
            "range": "stddev: 0.016357796556187184",
            "extra": "mean: 1.999319503999999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3691992080740186,
            "unit": "iter/sec",
            "range": "stddev: 0.16185588942084217",
            "extra": "mean: 2.708564856400005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6357147263263483,
            "unit": "iter/sec",
            "range": "stddev: 0.1437708089371791",
            "extra": "mean: 1.573032617599995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23797073732412521,
            "unit": "iter/sec",
            "range": "stddev: 0.11939016531306557",
            "extra": "mean: 4.202197342599993 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.27202319000045116,
            "unit": "iter/sec",
            "range": "stddev: 0.11174473467917338",
            "extra": "mean: 3.676157168799989 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3298321088111587,
            "unit": "iter/sec",
            "range": "stddev: 0.08071487718132164",
            "extra": "mean: 3.0318455155999913 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.32111288865519766,
            "unit": "iter/sec",
            "range": "stddev: 0.0648957802861331",
            "extra": "mean: 3.1141696123999965 sec\nrounds: 5"
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
          "id": "a0872de172fddac74893bf60e6d00ef7f7790931",
          "message": "Merge pull request #1407 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-05-31T01:11:49Z",
          "tree_id": "2243c56d7fbda707d37befcb64f7cd0b873acefa",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/a0872de172fddac74893bf60e6d00ef7f7790931"
        },
        "date": 1748654124462,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26776243238245606,
            "unit": "iter/sec",
            "range": "stddev: 0.07088806405281263",
            "extra": "mean: 3.734653853799995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5038783494385631,
            "unit": "iter/sec",
            "range": "stddev: 0.016850198436025147",
            "extra": "mean: 1.984606008800003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.36805510324906154,
            "unit": "iter/sec",
            "range": "stddev: 0.1259495971239335",
            "extra": "mean: 2.716984470999995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.616958726917808,
            "unit": "iter/sec",
            "range": "stddev: 0.13746391254878917",
            "extra": "mean: 1.6208539670000022 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24687613791460986,
            "unit": "iter/sec",
            "range": "stddev: 0.08708944257695353",
            "extra": "mean: 4.050614241000005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.26941454121239694,
            "unit": "iter/sec",
            "range": "stddev: 0.11176200388667011",
            "extra": "mean: 3.711752140400006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3229074820732641,
            "unit": "iter/sec",
            "range": "stddev: 0.17995173034086182",
            "extra": "mean: 3.0968622763999973 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.32273457170789527,
            "unit": "iter/sec",
            "range": "stddev: 0.11639498209846447",
            "extra": "mean: 3.098521471400011 sec\nrounds: 5"
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
          "id": "d698cda257c6fbbcceb1593eba2a46e2fd6fe397",
          "message": "Merge pull request #1412 from rsp2k/main",
          "timestamp": "2025-06-06T00:05:30+02:00",
          "tree_id": "19765b2ff5ce7c1fa1f26245f060b55cf042c66a",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/d698cda257c6fbbcceb1593eba2a46e2fd6fe397"
        },
        "date": 1749161346604,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27049769658938827,
            "unit": "iter/sec",
            "range": "stddev: 0.10380750546476518",
            "extra": "mean: 3.6968891514000064 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5125248026204599,
            "unit": "iter/sec",
            "range": "stddev: 0.028834328028505305",
            "extra": "mean: 1.9511250868000047 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3777217892269141,
            "unit": "iter/sec",
            "range": "stddev: 0.16394565018411422",
            "extra": "mean: 2.647451188999997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5621829293478665,
            "unit": "iter/sec",
            "range": "stddev: 0.13995021618312106",
            "extra": "mean: 1.7787804428000016 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24393051410576902,
            "unit": "iter/sec",
            "range": "stddev: 0.08010274782809157",
            "extra": "mean: 4.099528112200005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2754594623697884,
            "unit": "iter/sec",
            "range": "stddev: 0.10758004949533997",
            "extra": "mean: 3.6302982348 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.33071852154161285,
            "unit": "iter/sec",
            "range": "stddev: 0.18057077523466386",
            "extra": "mean: 3.023719371200002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.32091220158994727,
            "unit": "iter/sec",
            "range": "stddev: 0.15557302550601199",
            "extra": "mean: 3.116117103199997 sec\nrounds: 5"
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
          "id": "c9a09f2126e25da6116681499f9c52e1c078df11",
          "message": "Merge pull request #1413 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-06-07T01:34:08Z",
          "tree_id": "35069748103375d1efef37908dfd308b6d79711e",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/c9a09f2126e25da6116681499f9c52e1c078df11"
        },
        "date": 1749260258429,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.28302469689292065,
            "unit": "iter/sec",
            "range": "stddev: 0.10349292802276756",
            "extra": "mean: 3.5332605634000176 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5412021877139397,
            "unit": "iter/sec",
            "range": "stddev: 0.013038037126288251",
            "extra": "mean: 1.847738281000011 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3900320216414557,
            "unit": "iter/sec",
            "range": "stddev: 0.1628383760210284",
            "extra": "mean: 2.563892051200014 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6646124019265295,
            "unit": "iter/sec",
            "range": "stddev: 0.1931326714155604",
            "extra": "mean: 1.5046363822000217 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2688960852857434,
            "unit": "iter/sec",
            "range": "stddev: 0.0714998748053563",
            "extra": "mean: 3.7189087335999944 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.28847252011664737,
            "unit": "iter/sec",
            "range": "stddev: 0.06548035553620964",
            "extra": "mean: 3.4665346966000015 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.358391139240692,
            "unit": "iter/sec",
            "range": "stddev: 0.08441610381877962",
            "extra": "mean: 2.790247554999985 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3480211819659541,
            "unit": "iter/sec",
            "range": "stddev: 0.18065676472087797",
            "extra": "mean: 2.8733883217999847 sec\nrounds: 5"
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
          "id": "34a520cc2bfb89d3fe505e0d69e3e11dbc18d138",
          "message": "Merge pull request #1414 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-06-07T01:41:27Z",
          "tree_id": "35069748103375d1efef37908dfd308b6d79711e",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/34a520cc2bfb89d3fe505e0d69e3e11dbc18d138"
        },
        "date": 1749260709039,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.25753290596458756,
            "unit": "iter/sec",
            "range": "stddev: 0.09689808516154898",
            "extra": "mean: 3.882998936599995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.48989256381246177,
            "unit": "iter/sec",
            "range": "stddev: 0.030410296351054578",
            "extra": "mean: 2.041263888999987 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3607833871896099,
            "unit": "iter/sec",
            "range": "stddev: 0.16411582301750105",
            "extra": "mean: 2.7717462485999933 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5487059334300507,
            "unit": "iter/sec",
            "range": "stddev: 0.22956821631488988",
            "extra": "mean: 1.8224698132000072 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24653932614755403,
            "unit": "iter/sec",
            "range": "stddev: 0.050929858238526665",
            "extra": "mean: 4.0561480216000065 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.26424453714404983,
            "unit": "iter/sec",
            "range": "stddev: 0.1417755842834029",
            "extra": "mean: 3.7843734095999935 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32182926062780753,
            "unit": "iter/sec",
            "range": "stddev: 0.07911008723522092",
            "extra": "mean: 3.1072376640000128 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.32607199416247007,
            "unit": "iter/sec",
            "range": "stddev: 0.11331461042259652",
            "extra": "mean: 3.066807385800007 sec\nrounds: 5"
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
          "id": "bd7d3f8eaab93744eb81917ea0c63550b2663d06",
          "message": "Merge pull request #1406 from procrastinate-org/upgrade",
          "timestamp": "2025-06-13T14:02:57+02:00",
          "tree_id": "54578adde389efcb3ae779a5a61a8b16c96db1d7",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/bd7d3f8eaab93744eb81917ea0c63550b2663d06"
        },
        "date": 1749816394203,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26766149647016374,
            "unit": "iter/sec",
            "range": "stddev: 0.08836855440272268",
            "extra": "mean: 3.7360622024000008 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5157615546393504,
            "unit": "iter/sec",
            "range": "stddev: 0.025967520853176534",
            "extra": "mean: 1.9388804593999964 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3690356924580949,
            "unit": "iter/sec",
            "range": "stddev: 0.13582987104783434",
            "extra": "mean: 2.709764991399993 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.7191781452282421,
            "unit": "iter/sec",
            "range": "stddev: 0.013647158414739688",
            "extra": "mean: 1.3904760685999917 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23778177869874192,
            "unit": "iter/sec",
            "range": "stddev: 0.11418607378056787",
            "extra": "mean: 4.205536712999998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2677863699704114,
            "unit": "iter/sec",
            "range": "stddev: 0.0978473382696081",
            "extra": "mean: 3.734320010800002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32406350231547004,
            "unit": "iter/sec",
            "range": "stddev: 0.15910015896475363",
            "extra": "mean: 3.085814949400003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.31987459538097296,
            "unit": "iter/sec",
            "range": "stddev: 0.13723649825688533",
            "extra": "mean: 3.1262251345999914 sec\nrounds: 5"
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
          "id": "01d61b0c06295726dfd08324e053a64898ab562e",
          "message": "Merge pull request #1418 from procrastinate-org/renovate/major-all\n\nUpdate pre-commit hook PyCQA/doc8 to v2",
          "timestamp": "2025-06-14T02:00:04Z",
          "tree_id": "54578adde389efcb3ae779a5a61a8b16c96db1d7",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/01d61b0c06295726dfd08324e053a64898ab562e"
        },
        "date": 1749866650408,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.23774095878266008,
            "unit": "iter/sec",
            "range": "stddev: 0.3332509139755764",
            "extra": "mean: 4.206258799999995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.3424296471266752,
            "unit": "iter/sec",
            "range": "stddev: 0.3026670966045859",
            "extra": "mean: 2.920307889199995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.32535889589854283,
            "unit": "iter/sec",
            "range": "stddev: 0.17723774717663945",
            "extra": "mean: 3.073528994000003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5083531054172741,
            "unit": "iter/sec",
            "range": "stddev: 0.22700833002519508",
            "extra": "mean: 1.9671366011999964 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23691560404113898,
            "unit": "iter/sec",
            "range": "stddev: 0.1502551111811929",
            "extra": "mean: 4.220912354200005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.22229799927289368,
            "unit": "iter/sec",
            "range": "stddev: 0.32430278991863826",
            "extra": "mean: 4.498466037799995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.2969023108253452,
            "unit": "iter/sec",
            "range": "stddev: 0.08927232942082657",
            "extra": "mean: 3.368111205400004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.27738570448811783,
            "unit": "iter/sec",
            "range": "stddev: 0.17518898133138702",
            "extra": "mean: 3.6050884520000066 sec\nrounds: 5"
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
          "id": "e8666e09d6588291e537a4d4b1a82b4c3d338abd",
          "message": "Merge pull request #1352 from procrastinate-org/threads-safe-memory-connector",
          "timestamp": "2025-06-14T09:07:24+02:00",
          "tree_id": "6e5dc56acb2a92caea70ede500d4e4f1bbc5e3bd",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/e8666e09d6588291e537a4d4b1a82b4c3d338abd"
        },
        "date": 1749885078851,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.24440137142916207,
            "unit": "iter/sec",
            "range": "stddev: 0.06744723849167392",
            "extra": "mean: 4.0916300680000175 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.3957906661776492,
            "unit": "iter/sec",
            "range": "stddev: 0.10805394206266167",
            "extra": "mean: 2.5265881322000494 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.347315363592206,
            "unit": "iter/sec",
            "range": "stddev: 0.23081059438637064",
            "extra": "mean: 2.879227655400041 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5732113070708709,
            "unit": "iter/sec",
            "range": "stddev: 0.19601593864830086",
            "extra": "mean: 1.7445573519999698 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22705719038621744,
            "unit": "iter/sec",
            "range": "stddev: 0.12471599060687047",
            "extra": "mean: 4.404176755200001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2381616556197472,
            "unit": "iter/sec",
            "range": "stddev: 0.11663161823939584",
            "extra": "mean: 4.198828721599989 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3190326031239871,
            "unit": "iter/sec",
            "range": "stddev: 0.1494132369325736",
            "extra": "mean: 3.134475881799972 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3162587052604295,
            "unit": "iter/sec",
            "range": "stddev: 0.1572293121246467",
            "extra": "mean: 3.161968297999988 sec\nrounds: 5"
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
          "id": "f0f74fccf9d2be869e17b270e463852ae18fe848",
          "message": "Merge pull request #1424 from procrastinate-org/fix-pyright",
          "timestamp": "2025-06-21T18:53:10+02:00",
          "tree_id": "be96cdf5d66add19def40d1113aea4a9d9e7d66b",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/f0f74fccf9d2be869e17b270e463852ae18fe848"
        },
        "date": 1750524998058,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2730971869087783,
            "unit": "iter/sec",
            "range": "stddev: 0.09737312706944024",
            "extra": "mean: 3.66170011240001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5107899074635874,
            "unit": "iter/sec",
            "range": "stddev: 0.022665696640312212",
            "extra": "mean: 1.9577520725999988 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3829383725556826,
            "unit": "iter/sec",
            "range": "stddev: 0.18252404267271927",
            "extra": "mean: 2.611386248200006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6478131162395179,
            "unit": "iter/sec",
            "range": "stddev: 0.1516162728094173",
            "extra": "mean: 1.5436550679999925 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24359007770476446,
            "unit": "iter/sec",
            "range": "stddev: 0.2689424267326874",
            "extra": "mean: 4.105257527000004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2788364524176228,
            "unit": "iter/sec",
            "range": "stddev: 0.08623539840050305",
            "extra": "mean: 3.586331669799995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.34226659294837614,
            "unit": "iter/sec",
            "range": "stddev: 0.09421707195233593",
            "extra": "mean: 2.9216991099999916 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.32715239525645223,
            "unit": "iter/sec",
            "range": "stddev: 0.13415395469429722",
            "extra": "mean: 3.0566794390000043 sec\nrounds: 5"
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
          "id": "9e914c10910e87d0e2dac3ac267048aec277923d",
          "message": "Merge pull request #1423 from procrastinate-org/ewjoachim-patch-1",
          "timestamp": "2025-06-21T19:05:55+02:00",
          "tree_id": "64b2f7cd6be6196d8d4f918b212a759724b5741c",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/9e914c10910e87d0e2dac3ac267048aec277923d"
        },
        "date": 1750525780254,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2587842102308568,
            "unit": "iter/sec",
            "range": "stddev: 0.17186753333759908",
            "extra": "mean: 3.8642233971999986 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.45333324219763577,
            "unit": "iter/sec",
            "range": "stddev: 0.08647260330035404",
            "extra": "mean: 2.205882796400002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3789323313522566,
            "unit": "iter/sec",
            "range": "stddev: 0.025991767508479167",
            "extra": "mean: 2.638993607200007 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5501983483312347,
            "unit": "iter/sec",
            "range": "stddev: 0.18491277377031923",
            "extra": "mean: 1.8175263575999907 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2372140457615729,
            "unit": "iter/sec",
            "range": "stddev: 0.14091935072969655",
            "extra": "mean: 4.215601975800007 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2609576183538874,
            "unit": "iter/sec",
            "range": "stddev: 0.07368985893940275",
            "extra": "mean: 3.832039877999995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3122711217595685,
            "unit": "iter/sec",
            "range": "stddev: 0.09212503205251042",
            "extra": "mean: 3.2023454310000035 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.31378786539587816,
            "unit": "iter/sec",
            "range": "stddev: 0.11519015851586278",
            "extra": "mean: 3.1868663842000045 sec\nrounds: 5"
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
          "id": "33480841378c5b820208c094ebc905f9d8d66d02",
          "message": "Merge pull request #1411 from onlyann/lock-priority",
          "timestamp": "2025-06-22T22:14:16+02:00",
          "tree_id": "99d1c1be406be5f51ad694fcfe9cd7bfc1ca00df",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/33480841378c5b820208c094ebc905f9d8d66d02"
        },
        "date": 1750623473223,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2679808068402987,
            "unit": "iter/sec",
            "range": "stddev: 0.0881662194536989",
            "extra": "mean: 3.7316105275999973 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.513589934121627,
            "unit": "iter/sec",
            "range": "stddev: 0.026857199974811428",
            "extra": "mean: 1.9470786586000002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3591792218683767,
            "unit": "iter/sec",
            "range": "stddev: 0.2197281551412449",
            "extra": "mean: 2.784125414600001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.7144783849159284,
            "unit": "iter/sec",
            "range": "stddev: 0.011083058562548712",
            "extra": "mean: 1.3996224674000017 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23014209573937983,
            "unit": "iter/sec",
            "range": "stddev: 0.13484633962099848",
            "extra": "mean: 4.345141625600002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.26532417378022555,
            "unit": "iter/sec",
            "range": "stddev: 0.17327780750604718",
            "extra": "mean: 3.7689743296000016 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3085297782072107,
            "unit": "iter/sec",
            "range": "stddev: 0.24939767918594868",
            "extra": "mean: 3.241178228600006 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.33356722858366133,
            "unit": "iter/sec",
            "range": "stddev: 0.12236140659555979",
            "extra": "mean: 2.997896418800002 sec\nrounds: 5"
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
          "id": "df665c6e0e253a312997a43f77cb60295472ab09",
          "message": "Merge pull request #1421 from ticosax/doc-batch-defer",
          "timestamp": "2025-06-24T12:50:56+02:00",
          "tree_id": "d6d6ba1bb62897f3ced4bb9d9a2d2fc70d3e5e5c",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/df665c6e0e253a312997a43f77cb60295472ab09"
        },
        "date": 1750762470499,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.264463172769571,
            "unit": "iter/sec",
            "range": "stddev: 0.10755852420608958",
            "extra": "mean: 3.7812448119999997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5176952153927943,
            "unit": "iter/sec",
            "range": "stddev: 0.015683397035319808",
            "extra": "mean: 1.9316384819999997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.36873342854403596,
            "unit": "iter/sec",
            "range": "stddev: 0.19264008009543307",
            "extra": "mean: 2.7119862822000016 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.7315780849464412,
            "unit": "iter/sec",
            "range": "stddev: 0.010265883639097438",
            "extra": "mean: 1.3669080861999987 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.25005959397738325,
            "unit": "iter/sec",
            "range": "stddev: 0.0946511486444883",
            "extra": "mean: 3.999046723599997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2774600101192212,
            "unit": "iter/sec",
            "range": "stddev: 0.11113566632130148",
            "extra": "mean: 3.604122985399994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32352666813485836,
            "unit": "iter/sec",
            "range": "stddev: 0.2291926067461089",
            "extra": "mean: 3.0909353030000033 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.2990880037869096,
            "unit": "iter/sec",
            "range": "stddev: 0.2442518032850749",
            "extra": "mean: 3.3434975236000013 sec\nrounds: 5"
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
          "id": "cbaa756630081afbcbcc2e0de99f9e5ad52041ea",
          "message": "Merge pull request #1356 from procrastinate-org/check-migration-file-naming",
          "timestamp": "2025-07-06T09:39:27+02:00",
          "tree_id": "2acb95743805144ee42241d9974b22c6dc1f0a0c",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/cbaa756630081afbcbcc2e0de99f9e5ad52041ea"
        },
        "date": 1751787801927,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.24703713502213895,
            "unit": "iter/sec",
            "range": "stddev: 0.09165125281577742",
            "extra": "mean: 4.047974406400002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.44692487939222364,
            "unit": "iter/sec",
            "range": "stddev: 0.04490321844791391",
            "extra": "mean: 2.2375124906000026 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.34321258200494514,
            "unit": "iter/sec",
            "range": "stddev: 0.2150444639199186",
            "extra": "mean: 2.9136460969999973 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5632774328160804,
            "unit": "iter/sec",
            "range": "stddev: 0.2192527107430954",
            "extra": "mean: 1.775324097400005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22368438085902878,
            "unit": "iter/sec",
            "range": "stddev: 0.22189718969421035",
            "extra": "mean: 4.4705848309999965 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.23673985651172264,
            "unit": "iter/sec",
            "range": "stddev: 0.1585217384924644",
            "extra": "mean: 4.2240458144000055 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.2962714748564798,
            "unit": "iter/sec",
            "range": "stddev: 0.1706656458177988",
            "extra": "mean: 3.3752827553999962 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.31090814603673644,
            "unit": "iter/sec",
            "range": "stddev: 0.09044490439345713",
            "extra": "mean: 3.2163840438000024 sec\nrounds: 5"
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
          "id": "41aec8f73affa2c9dfb3edde03c4c3ee40d8b99a",
          "message": "Merge pull request #1325 from ticosax/retry-failed-job",
          "timestamp": "2025-07-18T11:31:03+02:00",
          "tree_id": "b524aac806cf55a3ed1d29874791d3ea0589bee6",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/41aec8f73affa2c9dfb3edde03c4c3ee40d8b99a"
        },
        "date": 1752831269073,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.28963045836822493,
            "unit": "iter/sec",
            "range": "stddev: 0.07535499217095282",
            "extra": "mean: 3.4526755426000078 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5469286220870603,
            "unit": "iter/sec",
            "range": "stddev: 0.012075632912007181",
            "extra": "mean: 1.828392151400004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.39487667965913364,
            "unit": "iter/sec",
            "range": "stddev: 0.2092392853108732",
            "extra": "mean: 2.5324362047999953 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.680885515176573,
            "unit": "iter/sec",
            "range": "stddev: 0.20609413723514064",
            "extra": "mean: 1.4686756844000002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2741501137817113,
            "unit": "iter/sec",
            "range": "stddev: 0.05301571802299985",
            "extra": "mean: 3.647636640400003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2913494735164008,
            "unit": "iter/sec",
            "range": "stddev: 0.07342834239591023",
            "extra": "mean: 3.432304125799999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.34076746312645523,
            "unit": "iter/sec",
            "range": "stddev: 0.043050661970341006",
            "extra": "mean: 2.9345524682000246 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3502084945855362,
            "unit": "iter/sec",
            "range": "stddev: 0.222844838122282",
            "extra": "mean: 2.855441873799998 sec\nrounds: 5"
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
          "id": "97236af309a419742d52219eb07ad4830c005b60",
          "message": "Merge pull request #1425 from woolfred/fix-reconnect-on-disconnect",
          "timestamp": "2025-07-31T23:49:22+02:00",
          "tree_id": "e69514625b8a8584618019a174c24fce48088c0c",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/97236af309a419742d52219eb07ad4830c005b60"
        },
        "date": 1753998778695,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27281905383379595,
            "unit": "iter/sec",
            "range": "stddev: 0.10990210524740879",
            "extra": "mean: 3.6654331358000007 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.49352703459135466,
            "unit": "iter/sec",
            "range": "stddev: 0.02612603687578367",
            "extra": "mean: 2.0262314522 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3633759806180852,
            "unit": "iter/sec",
            "range": "stddev: 0.2402071751669385",
            "extra": "mean: 2.7519705576000035 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.7107338749491647,
            "unit": "iter/sec",
            "range": "stddev: 0.048071493669223246",
            "extra": "mean: 1.4069963951999966 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23332471908736757,
            "unit": "iter/sec",
            "range": "stddev: 0.1591256615627447",
            "extra": "mean: 4.285872512399999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2777336660956443,
            "unit": "iter/sec",
            "range": "stddev: 0.08814962633000091",
            "extra": "mean: 3.6005717782000035 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32215143052707806,
            "unit": "iter/sec",
            "range": "stddev: 0.21888551264160547",
            "extra": "mean: 3.1041302481999877 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3223760035156617,
            "unit": "iter/sec",
            "range": "stddev: 0.10960264816200066",
            "extra": "mean: 3.1019678546000025 sec\nrounds: 5"
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
          "id": "415c4b5c1b92c84ff80b67f00f56993d4052d6da",
          "message": "Merge pull request #1436 from procrastinate-org/revert-1425-fix-reconnect-on-disconnect",
          "timestamp": "2025-08-07T16:00:33+02:00",
          "tree_id": "b524aac806cf55a3ed1d29874791d3ea0589bee6",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/415c4b5c1b92c84ff80b67f00f56993d4052d6da"
        },
        "date": 1754575464102,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2517152285465534,
            "unit": "iter/sec",
            "range": "stddev: 0.06593042363004956",
            "extra": "mean: 3.9727433488000314 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4480017388144371,
            "unit": "iter/sec",
            "range": "stddev: 0.07005615214033305",
            "extra": "mean: 2.2321341936000865 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3618111735950907,
            "unit": "iter/sec",
            "range": "stddev: 0.023069191370474994",
            "extra": "mean: 2.763872630199967 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5776171793152909,
            "unit": "iter/sec",
            "range": "stddev: 0.20546190523619132",
            "extra": "mean: 1.7312504472 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22729290386750398,
            "unit": "iter/sec",
            "range": "stddev: 0.2741491604942177",
            "extra": "mean: 4.399609415800024 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2394335199903811,
            "unit": "iter/sec",
            "range": "stddev: 0.2199270908547694",
            "extra": "mean: 4.176524657199934 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.31254022640792867,
            "unit": "iter/sec",
            "range": "stddev: 0.1696095368132795",
            "extra": "mean: 3.1995881345999804 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.2923238761525891,
            "unit": "iter/sec",
            "range": "stddev: 0.2837389763398927",
            "extra": "mean: 3.420863232800093 sec\nrounds: 5"
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
          "id": "d4e4485d4aada0cbbaba0245a3f10ec2b02e1ea0",
          "message": "Merge pull request #1437 from procrastinate-org/renovate/major-all\n\nUpdate actions/download-artifact action to v5",
          "timestamp": "2025-08-09T00:57:16Z",
          "tree_id": "6c3ad36ae5f891b54f95e3b10f41c4bd7302b427",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/d4e4485d4aada0cbbaba0245a3f10ec2b02e1ea0"
        },
        "date": 1754701250881,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2754213595818402,
            "unit": "iter/sec",
            "range": "stddev: 0.07711541510557347",
            "extra": "mean: 3.630800463399987 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5170379700119134,
            "unit": "iter/sec",
            "range": "stddev: 0.026472342148984373",
            "extra": "mean: 1.9340939311999819 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.37115147503523505,
            "unit": "iter/sec",
            "range": "stddev: 0.24685637835501445",
            "extra": "mean: 2.6943177307999804 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6071826105636993,
            "unit": "iter/sec",
            "range": "stddev: 0.23176041420943078",
            "extra": "mean: 1.6469509874000097 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.233085005749174,
            "unit": "iter/sec",
            "range": "stddev: 0.16249503000736176",
            "extra": "mean: 4.290280263999966 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2757033352762802,
            "unit": "iter/sec",
            "range": "stddev: 0.12716864021540125",
            "extra": "mean: 3.6270870607999997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32150325219042225,
            "unit": "iter/sec",
            "range": "stddev: 0.2113947862712408",
            "extra": "mean: 3.110388442999988 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3194925034262376,
            "unit": "iter/sec",
            "range": "stddev: 0.07063349536840507",
            "extra": "mean: 3.1299638936000065 sec\nrounds: 5"
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
          "id": "2bfa76bc1a8016940399b7cdd5e01da09d0ce94c",
          "message": "Merge pull request #1417 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-08-14T11:19:52Z",
          "tree_id": "5ad8761b52ea97d345dd0bf4c12576e67ffb5dfa",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/2bfa76bc1a8016940399b7cdd5e01da09d0ce94c"
        },
        "date": 1755170636558,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.23830321999934903,
            "unit": "iter/sec",
            "range": "stddev: 0.09745748369041371",
            "extra": "mean: 4.1963344012 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.43067168849241416,
            "unit": "iter/sec",
            "range": "stddev: 0.12925477679516983",
            "extra": "mean: 2.3219543488 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3075196733767525,
            "unit": "iter/sec",
            "range": "stddev: 0.3216271041322882",
            "extra": "mean: 3.251824473599993 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5798443176756861,
            "unit": "iter/sec",
            "range": "stddev: 0.22767253898956177",
            "extra": "mean: 1.7246008446000018 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.21103633262597496,
            "unit": "iter/sec",
            "range": "stddev: 0.12474831444552636",
            "extra": "mean: 4.738520555000003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2431871154059332,
            "unit": "iter/sec",
            "range": "stddev: 0.1275356026351505",
            "extra": "mean: 4.112059959800002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.30487837338300355,
            "unit": "iter/sec",
            "range": "stddev: 0.12599949635572702",
            "extra": "mean: 3.279996507800013 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.283031067706352,
            "unit": "iter/sec",
            "range": "stddev: 0.39545187269819265",
            "extra": "mean: 3.533181032399989 sec\nrounds: 5"
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
          "id": "8a4b434357e9c26ac2aae5356d39dfb073237fd5",
          "message": "Merge pull request #1440 from procrastinate-org/renovate/major-all\n\nUpdate all dependencies (major)",
          "timestamp": "2025-08-20T21:11:13+02:00",
          "tree_id": "b2e76620577a21afb6ba1dfd1f66ef0e9d765e17",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/8a4b434357e9c26ac2aae5356d39dfb073237fd5"
        },
        "date": 1755717290049,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27729837562650467,
            "unit": "iter/sec",
            "range": "stddev: 0.11967290618363807",
            "extra": "mean: 3.6062237931999563 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5285218727056172,
            "unit": "iter/sec",
            "range": "stddev: 0.04836021448028548",
            "extra": "mean: 1.8920692815999929 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3724862176836467,
            "unit": "iter/sec",
            "range": "stddev: 0.24127513721815416",
            "extra": "mean: 2.684663089600008 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6077616173788031,
            "unit": "iter/sec",
            "range": "stddev: 0.23952183637238783",
            "extra": "mean: 1.64538195800003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.23640740692939227,
            "unit": "iter/sec",
            "range": "stddev: 0.1522788394848518",
            "extra": "mean: 4.229985908600019 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.28747539776706105,
            "unit": "iter/sec",
            "range": "stddev: 0.06419982339552019",
            "extra": "mean: 3.4785585401999923 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3363013135612435,
            "unit": "iter/sec",
            "range": "stddev: 0.2710011965048684",
            "extra": "mean: 2.9735239194000087 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.31334892052819324,
            "unit": "iter/sec",
            "range": "stddev: 0.2587751262396172",
            "extra": "mean: 3.1913306046000116 sec\nrounds: 5"
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
          "id": "53d13dd67ae39443ea4c69410005825cb80071f1",
          "message": "Merge pull request #1441 from ozamosi/fix-migration-schema",
          "timestamp": "2025-08-23T11:07:26+02:00",
          "tree_id": "ad49d9d1c923fb3451ff7af9d08dea69073a9cb7",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/53d13dd67ae39443ea4c69410005825cb80071f1"
        },
        "date": 1755940261797,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2745630811711811,
            "unit": "iter/sec",
            "range": "stddev: 0.07220292930932916",
            "extra": "mean: 3.6421502692000045 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5242732506897935,
            "unit": "iter/sec",
            "range": "stddev: 0.022306323793903782",
            "extra": "mean: 1.9074022919999947 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3754495676205514,
            "unit": "iter/sec",
            "range": "stddev: 0.15892301293891284",
            "extra": "mean: 2.6634735694000087 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6284600456997324,
            "unit": "iter/sec",
            "range": "stddev: 0.20193510230560888",
            "extra": "mean: 1.591191049999992 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2577467991592863,
            "unit": "iter/sec",
            "range": "stddev: 0.06381696450137024",
            "extra": "mean: 3.879776599600001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2724972389609655,
            "unit": "iter/sec",
            "range": "stddev: 0.08870939231585724",
            "extra": "mean: 3.6697619536000046 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3218757294019887,
            "unit": "iter/sec",
            "range": "stddev: 0.21355250384885313",
            "extra": "mean: 3.106789076199982 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.2987330967933241,
            "unit": "iter/sec",
            "range": "stddev: 0.12776877296635836",
            "extra": "mean: 3.3474697338000055 sec\nrounds: 5"
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
          "id": "b5042b97aa57faae344790b4cfa2e9ca2701264c",
          "message": "Merge pull request #1420 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-08-23T09:25:20Z",
          "tree_id": "35c66074d78e4ca6562a9417cc0fad8b1800224a",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/b5042b97aa57faae344790b4cfa2e9ca2701264c"
        },
        "date": 1755941350307,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.25991258911840753,
            "unit": "iter/sec",
            "range": "stddev: 0.09528626203471793",
            "extra": "mean: 3.8474473413999704 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.47121073327803203,
            "unit": "iter/sec",
            "range": "stddev: 0.03547120966799174",
            "extra": "mean: 2.1221927460000414 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.37089268001447373,
            "unit": "iter/sec",
            "range": "stddev: 0.06784637945429015",
            "extra": "mean: 2.6961977248000037 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5801262844769731,
            "unit": "iter/sec",
            "range": "stddev: 0.2212666448118315",
            "extra": "mean: 1.7237626129999852 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.22803221266623544,
            "unit": "iter/sec",
            "range": "stddev: 0.27336050599802675",
            "extra": "mean: 4.385345334800013 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.23951912122746682,
            "unit": "iter/sec",
            "range": "stddev: 0.26861683766712047",
            "extra": "mean: 4.175032017800026 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3143591395002133,
            "unit": "iter/sec",
            "range": "stddev: 0.10698797177495513",
            "extra": "mean: 3.181075000999999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.303356882838554,
            "unit": "iter/sec",
            "range": "stddev: 0.13212763538633737",
            "extra": "mean: 3.2964473746000293 sec\nrounds: 5"
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
          "id": "1b83694331984718a943622ad3ddb8d92636a0d9",
          "message": "Merge pull request #1439 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-08-23T09:26:38Z",
          "tree_id": "20ec6d6fe5726df28d602f33648f23a4a70d3e05",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/1b83694331984718a943622ad3ddb8d92636a0d9"
        },
        "date": 1755941421467,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26379096005321623,
            "unit": "iter/sec",
            "range": "stddev: 0.1651853363822795",
            "extra": "mean: 3.790880475199998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4509877637322565,
            "unit": "iter/sec",
            "range": "stddev: 0.08593718864706322",
            "extra": "mean: 2.217355060199998 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3732259662511768,
            "unit": "iter/sec",
            "range": "stddev: 0.024649222734460265",
            "extra": "mean: 2.6793419815999924 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5201263278372759,
            "unit": "iter/sec",
            "range": "stddev: 0.20750320850045964",
            "extra": "mean: 1.922609847800004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2316960749965153,
            "unit": "iter/sec",
            "range": "stddev: 0.18236768158822073",
            "extra": "mean: 4.315998879200004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.24582436926146478,
            "unit": "iter/sec",
            "range": "stddev: 0.21011804767196113",
            "extra": "mean: 4.067944943800001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32598568267726097,
            "unit": "iter/sec",
            "range": "stddev: 0.0684818370886478",
            "extra": "mean: 3.067619386800004 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.31188262261768446,
            "unit": "iter/sec",
            "range": "stddev: 0.2201319554104522",
            "extra": "mean: 3.2063344588000064 sec\nrounds: 5"
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
          "id": "76a87d431cbdb4818f5e79003352dee8dd58d8b5",
          "message": "Merge pull request #1442 from procrastinate-org/upgrade",
          "timestamp": "2025-08-23T11:38:22+02:00",
          "tree_id": "5d70a51e22eeedc7f12ed326eaa44e61338a094d",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/76a87d431cbdb4818f5e79003352dee8dd58d8b5"
        },
        "date": 1755942111812,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2764196711445587,
            "unit": "iter/sec",
            "range": "stddev: 0.06007521206279668",
            "extra": "mean: 3.6176875396000012 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5319184127100194,
            "unit": "iter/sec",
            "range": "stddev: 0.016342819178793322",
            "extra": "mean: 1.8799875621999944 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.3802589911545061,
            "unit": "iter/sec",
            "range": "stddev: 0.22236935937432842",
            "extra": "mean: 2.6297866013999966 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6610953498641606,
            "unit": "iter/sec",
            "range": "stddev: 0.19785846818694722",
            "extra": "mean: 1.5126411041999859 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2584640093609254,
            "unit": "iter/sec",
            "range": "stddev: 0.0654977854525239",
            "extra": "mean: 3.8690106312000125 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.28068757875321965,
            "unit": "iter/sec",
            "range": "stddev: 0.08625716420435331",
            "extra": "mean: 3.5626799177999944 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.35057884674277934,
            "unit": "iter/sec",
            "range": "stddev: 0.08029076935545702",
            "extra": "mean: 2.8524253795999925 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.32627683660375495,
            "unit": "iter/sec",
            "range": "stddev: 0.20717469424975643",
            "extra": "mean: 3.0648819892000008 sec\nrounds: 5"
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
          "id": "873a0919d51a00ccdd62d46616a865d987915cf4",
          "message": "Merge pull request #1444 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-08-25T02:14:39Z",
          "tree_id": "2b6f39cfdbeecaf9b3f0e922bdf33e44f01e68c4",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/873a0919d51a00ccdd62d46616a865d987915cf4"
        },
        "date": 1756088315151,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2696992927403846,
            "unit": "iter/sec",
            "range": "stddev: 0.08655376286958896",
            "extra": "mean: 3.7078332310000177 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.48648851738934035,
            "unit": "iter/sec",
            "range": "stddev: 0.02496064650805143",
            "extra": "mean: 2.0555469743999994 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.34930606272491754,
            "unit": "iter/sec",
            "range": "stddev: 0.2725535944620909",
            "extra": "mean: 2.8628189049999717 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5839361706808738,
            "unit": "iter/sec",
            "range": "stddev: 0.23592966541258112",
            "extra": "mean: 1.71251593960003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24531302413051706,
            "unit": "iter/sec",
            "range": "stddev: 0.2424783602553575",
            "extra": "mean: 4.076424411400012 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.25260321378682615,
            "unit": "iter/sec",
            "range": "stddev: 0.06479982663325509",
            "extra": "mean: 3.9587778199999777 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.21028944488218276,
            "unit": "iter/sec",
            "range": "stddev: 3.1241914454682953",
            "extra": "mean: 4.755350419800015 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3019807631412213,
            "unit": "iter/sec",
            "range": "stddev: 0.2608248823388625",
            "extra": "mean: 3.311469212799989 sec\nrounds: 5"
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
          "id": "a20b9a4b022a42278adfb4f7e7b1d6926f67ab08",
          "message": "Merge pull request #1445 from Melebius/fix-docs",
          "timestamp": "2025-08-25T18:17:51+02:00",
          "tree_id": "d0813699f9fc3b5aa4f550a41c30dd4a62093755",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/a20b9a4b022a42278adfb4f7e7b1d6926f67ab08"
        },
        "date": 1756138888692,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27541942395427915,
            "unit": "iter/sec",
            "range": "stddev: 0.06736319992652183",
            "extra": "mean: 3.6308259804000045 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5043387787527247,
            "unit": "iter/sec",
            "range": "stddev: 0.0186267872242268",
            "extra": "mean: 1.9827941894000105 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.36281778128265435,
            "unit": "iter/sec",
            "range": "stddev: 0.23743644316969514",
            "extra": "mean: 2.7562044960000094 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.61090439197289,
            "unit": "iter/sec",
            "range": "stddev: 0.19834736735177455",
            "extra": "mean: 1.6369173526000396 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.25748465852512903,
            "unit": "iter/sec",
            "range": "stddev: 0.05496284672458298",
            "extra": "mean: 3.88372653240001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2720550248054972,
            "unit": "iter/sec",
            "range": "stddev: 0.07726623662327795",
            "extra": "mean: 3.67572699939999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32503803516753405,
            "unit": "iter/sec",
            "range": "stddev: 0.23797482382889784",
            "extra": "mean: 3.0765630227999963 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3222411628903827,
            "unit": "iter/sec",
            "range": "stddev: 0.11951034774876618",
            "extra": "mean: 3.103265861599971 sec\nrounds: 5"
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
          "id": "7d8990b7f593565510fb4587939522a4778075cf",
          "message": "Merge pull request #1448 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-09-06T02:42:46Z",
          "tree_id": "70c4a44d88274d2cd11fb8a50878f8521bc68234",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/7d8990b7f593565510fb4587939522a4778075cf"
        },
        "date": 1757126790320,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26907631094410284,
            "unit": "iter/sec",
            "range": "stddev: 0.06171225016750847",
            "extra": "mean: 3.71641783140002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.46761785699691183,
            "unit": "iter/sec",
            "range": "stddev: 0.02479715156842268",
            "extra": "mean: 2.1384983166000096 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.37874836047087795,
            "unit": "iter/sec",
            "range": "stddev: 0.05270155771762603",
            "extra": "mean: 2.640275455599999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5644051731836597,
            "unit": "iter/sec",
            "range": "stddev: 0.2198933013231863",
            "extra": "mean: 1.7717768148000232 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2379184279958231,
            "unit": "iter/sec",
            "range": "stddev: 0.20534932791229596",
            "extra": "mean: 4.203121247999991 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.26159284313288483,
            "unit": "iter/sec",
            "range": "stddev: 0.11449203959231961",
            "extra": "mean: 3.82273455200002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.30953555358866536,
            "unit": "iter/sec",
            "range": "stddev: 0.0778157312053642",
            "extra": "mean: 3.2306466523999915 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3140803544289348,
            "unit": "iter/sec",
            "range": "stddev: 0.25115117031494444",
            "extra": "mean: 3.183898597600012 sec\nrounds: 5"
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
          "id": "660d8fd4df4d80a4d9b87528475713424eb8087b",
          "message": "Merge pull request #1449 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-09-06T02:49:57Z",
          "tree_id": "70c4a44d88274d2cd11fb8a50878f8521bc68234",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/660d8fd4df4d80a4d9b87528475713424eb8087b"
        },
        "date": 1757127215436,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2559023545270654,
            "unit": "iter/sec",
            "range": "stddev: 0.07689073657690527",
            "extra": "mean: 3.907740520200002 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4822799171475047,
            "unit": "iter/sec",
            "range": "stddev: 0.05490010753081872",
            "extra": "mean: 2.073484639200001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.35814457547144346,
            "unit": "iter/sec",
            "range": "stddev: 0.22005010494513788",
            "extra": "mean: 2.7921684942000042 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6909984882480166,
            "unit": "iter/sec",
            "range": "stddev: 0.014423801922910472",
            "extra": "mean: 1.4471811690000038 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.221134587283232,
            "unit": "iter/sec",
            "range": "stddev: 0.13680637454289768",
            "extra": "mean: 4.522132933999996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.25903921725063667,
            "unit": "iter/sec",
            "range": "stddev: 0.11717365357919184",
            "extra": "mean: 3.860419324200001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.30215325172293794,
            "unit": "iter/sec",
            "range": "stddev: 0.1162625254201356",
            "extra": "mean: 3.3095788124000025 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3261771343453494,
            "unit": "iter/sec",
            "range": "stddev: 0.2768306456004095",
            "extra": "mean: 3.065818828800002 sec\nrounds: 5"
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
          "id": "660d8fd4df4d80a4d9b87528475713424eb8087b",
          "message": "Merge pull request #1449 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-09-06T02:49:57Z",
          "tree_id": "70c4a44d88274d2cd11fb8a50878f8521bc68234",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/660d8fd4df4d80a4d9b87528475713424eb8087b"
        },
        "date": 1757277297219,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2702857277649408,
            "unit": "iter/sec",
            "range": "stddev: 0.06283854458044333",
            "extra": "mean: 3.699788398999999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5186038368015956,
            "unit": "iter/sec",
            "range": "stddev: 0.013694640647644666",
            "extra": "mean: 1.9282541490000085 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.36974193082891915,
            "unit": "iter/sec",
            "range": "stddev: 0.16906220103943226",
            "extra": "mean: 2.704589110999973 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6176065167412628,
            "unit": "iter/sec",
            "range": "stddev: 0.1990775323683546",
            "extra": "mean: 1.619153899600019 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.256388748799599,
            "unit": "iter/sec",
            "range": "stddev: 0.061738941811969705",
            "extra": "mean: 3.9003271582000254 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.27488385088414324,
            "unit": "iter/sec",
            "range": "stddev: 0.09206422153691282",
            "extra": "mean: 3.637900141399996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3240080430919382,
            "unit": "iter/sec",
            "range": "stddev: 0.23873513692669193",
            "extra": "mean: 3.0863431365999987 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3034110778648025,
            "unit": "iter/sec",
            "range": "stddev: 0.14743026530738101",
            "extra": "mean: 3.2958585659999926 sec\nrounds: 5"
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
          "id": "0ece824926a898f15080eac85cfade57178a316a",
          "message": "Merge pull request #1452 from procrastinate-org/renovate/lock-file-maintenance\n\nLock file maintenance",
          "timestamp": "2025-09-08T11:40:57Z",
          "tree_id": "7a624a157603bc97aee62cad44c73882ea0aded5",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/0ece824926a898f15080eac85cfade57178a316a"
        },
        "date": 1757331877577,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27306024612487545,
            "unit": "iter/sec",
            "range": "stddev: 0.10046488183700622",
            "extra": "mean: 3.6621954832000028 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5132316764026565,
            "unit": "iter/sec",
            "range": "stddev: 0.03363338273773515",
            "extra": "mean: 1.9484378030000016 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.35548785054662063,
            "unit": "iter/sec",
            "range": "stddev: 0.15462827890747624",
            "extra": "mean: 2.8130356591999885 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6111937565339275,
            "unit": "iter/sec",
            "range": "stddev: 0.1882319955564408",
            "extra": "mean: 1.636142367800005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24674621366708868,
            "unit": "iter/sec",
            "range": "stddev: 0.2408958443780942",
            "extra": "mean: 4.052747092399988 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.27363320554911913,
            "unit": "iter/sec",
            "range": "stddev: 0.11254991119544498",
            "extra": "mean: 3.6545272274000125 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3316610999908128,
            "unit": "iter/sec",
            "range": "stddev: 0.10729818166053585",
            "extra": "mean: 3.0151259826000114 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3409174435336712,
            "unit": "iter/sec",
            "range": "stddev: 0.1158141166279907",
            "extra": "mean: 2.9332614654000055 sec\nrounds: 5"
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
          "id": "453bac747ea1d5b1c2dac96dfde6a0c22fd47ada",
          "message": "Merge pull request #1459 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-09-20T01:28:10Z",
          "tree_id": "0f123740777fee1e8328cfe9d8035e88142db71a",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/453bac747ea1d5b1c2dac96dfde6a0c22fd47ada"
        },
        "date": 1758331897664,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.28215794367786223,
            "unit": "iter/sec",
            "range": "stddev: 0.0867278601588399",
            "extra": "mean: 3.5441142891999986 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.508806096903788,
            "unit": "iter/sec",
            "range": "stddev: 0.01633722718554236",
            "extra": "mean: 1.9653852540000003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.37500338989001786,
            "unit": "iter/sec",
            "range": "stddev: 0.23465024994664566",
            "extra": "mean: 2.6666425610000033 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.6168960938011889,
            "unit": "iter/sec",
            "range": "stddev: 0.22184444227633218",
            "extra": "mean: 1.6210185314 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24371292867135777,
            "unit": "iter/sec",
            "range": "stddev: 0.23439730983194917",
            "extra": "mean: 4.103188146199995 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.28308495427268066,
            "unit": "iter/sec",
            "range": "stddev: 0.07880357653585097",
            "extra": "mean: 3.5325084746000073 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.35285589533532563,
            "unit": "iter/sec",
            "range": "stddev: 0.08013598022977413",
            "extra": "mean: 2.8340181168000074 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3313888145322166,
            "unit": "iter/sec",
            "range": "stddev: 0.2590495500887215",
            "extra": "mean: 3.017603359399999 sec\nrounds: 5"
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
          "id": "217220f7dd7a48de6e557373fe07a4c9da02409c",
          "message": "Merge pull request #1460 from procrastinate-org/renovate/all\n\nUpdate all dependencies",
          "timestamp": "2025-09-20T01:35:13Z",
          "tree_id": "0f123740777fee1e8328cfe9d8035e88142db71a",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/217220f7dd7a48de6e557373fe07a4c9da02409c"
        },
        "date": 1758332334040,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.26016751288472656,
            "unit": "iter/sec",
            "range": "stddev: 0.09974786310056276",
            "extra": "mean: 3.8436774404000005 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.4668526858249021,
            "unit": "iter/sec",
            "range": "stddev: 0.03669435832258878",
            "extra": "mean: 2.1420033136 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.36430981069628987,
            "unit": "iter/sec",
            "range": "stddev: 0.1332045909774853",
            "extra": "mean: 2.7449164712 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5757696980756093,
            "unit": "iter/sec",
            "range": "stddev: 0.2145553706904258",
            "extra": "mean: 1.736805537600003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.24730234521238245,
            "unit": "iter/sec",
            "range": "stddev: 0.08474485373055247",
            "extra": "mean: 4.043633306999993 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2590633921114903,
            "unit": "iter/sec",
            "range": "stddev: 0.08587460148667242",
            "extra": "mean: 3.8600590838000017 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.297475274436902,
            "unit": "iter/sec",
            "range": "stddev: 0.14419034386474916",
            "extra": "mean: 3.3616239261999965 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3102912074573083,
            "unit": "iter/sec",
            "range": "stddev: 0.21005210687804285",
            "extra": "mean: 3.2227790410000123 sec\nrounds: 5"
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
          "id": "4cf201624aa5b74ae6e0c260171c2e91dc38329e",
          "message": "Merge pull request #1465 from jakajancar/clamp-datetime-from-timedelta-params",
          "timestamp": "2025-09-26T07:45:09+02:00",
          "tree_id": "4c8511c706255a15475f48638aaccffc9331dc8e",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/4cf201624aa5b74ae6e0c260171c2e91dc38329e"
        },
        "date": 1758865735637,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.2713709884191587,
            "unit": "iter/sec",
            "range": "stddev: 0.10351649870711391",
            "extra": "mean: 3.6849922897999816 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5031947112143373,
            "unit": "iter/sec",
            "range": "stddev: 0.058433258199990776",
            "extra": "mean: 1.9873022861999972 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.37262834256085803,
            "unit": "iter/sec",
            "range": "stddev: 0.1249087496638319",
            "extra": "mean: 2.68363912719999 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.5944268660333475,
            "unit": "iter/sec",
            "range": "stddev: 0.20061452847253372",
            "extra": "mean: 1.682292738000001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.243898978300146,
            "unit": "iter/sec",
            "range": "stddev: 0.2757150328853065",
            "extra": "mean: 4.100058175599997 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.23742859312387307,
            "unit": "iter/sec",
            "range": "stddev: 0.1288660753139197",
            "extra": "mean: 4.211792635600011 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.3344220905100577,
            "unit": "iter/sec",
            "range": "stddev: 0.09927438488476178",
            "extra": "mean: 2.9902330868000035 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3188245918767125,
            "unit": "iter/sec",
            "range": "stddev: 0.2355325376183478",
            "extra": "mean: 3.136520913000004 sec\nrounds: 5"
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
          "id": "7873c2c624ccacbe9ab673d474f394b5f706ebe3",
          "message": "Merge pull request #1468 from procrastinate-org/renovate/major-all\n\nUpdate postgres Docker tag to v18",
          "timestamp": "2025-09-27T00:40:55Z",
          "tree_id": "5333bb4b4e909c51ad6c4737ca1588cf89131293",
          "url": "https://github.com/procrastinate-org/procrastinate/commit/7873c2c624ccacbe9ab673d474f394b5f706ebe3"
        },
        "date": 1758933868825,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[psycopg_connector]",
            "value": 0.27674749589636183,
            "unit": "iter/sec",
            "range": "stddev: 0.08536879392824659",
            "extra": "mean: 3.613402162 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_jobs[aiopg_connector]",
            "value": 0.5230378299645647,
            "unit": "iter/sec",
            "range": "stddev: 0.02815333068461643",
            "extra": "mean: 1.9119075957999996 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[psycopg_connector]",
            "value": 0.37767185530817793,
            "unit": "iter/sec",
            "range": "stddev: 0.19958988247847873",
            "extra": "mean: 2.6478012219999982 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_async.py::test_benchmark_1000_async_batch_jobs[aiopg_connector]",
            "value": 0.7410457747232664,
            "unit": "iter/sec",
            "range": "stddev: 0.02219360328550737",
            "extra": "mean: 1.3494443044000035 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[sync_psycopg_connector]",
            "value": 0.2425610778729385,
            "unit": "iter/sec",
            "range": "stddev: 0.1350762949425182",
            "extra": "mean: 4.122672972800001 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_jobs[psycopg2_connector]",
            "value": 0.2694985410220822,
            "unit": "iter/sec",
            "range": "stddev: 0.10457451595527173",
            "extra": "mean: 3.710595226999993 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[sync_psycopg_connector]",
            "value": 0.32721005340198533,
            "unit": "iter/sec",
            "range": "stddev: 0.23239484415299624",
            "extra": "mean: 3.056140817200003 sec\nrounds: 5"
          },
          {
            "name": "tests/benchmarks/test_benchmark_sync.py::test_benchmark_1000_sync_batch_jobs[psycopg2_connector]",
            "value": 0.3201892806770944,
            "unit": "iter/sec",
            "range": "stddev: 0.11137423825980158",
            "extra": "mean: 3.123152648600012 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}