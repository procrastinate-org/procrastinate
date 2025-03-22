window.BENCHMARK_DATA = {
  "lastUpdate": 1742658614650,
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
      }
    ]
  }
}