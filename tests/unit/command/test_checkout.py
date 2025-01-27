import logging

from dvc.cli import parse_args
from dvc.command.checkout import CmdCheckout, log_summary, log_changes


def test_checkout(tmp_dir, dvc, mocker):
    cli_args = parse_args(
        ["checkout", "foo.dvc", "bar.dvc", "--relink", "--with-deps"]
    )
    assert cli_args.func == CmdCheckout

    cmd = cli_args.func(cli_args)
    m = mocker.patch("dvc.repo.Repo.checkout")

    assert cmd.run() == 0
    m.assert_called_once_with(
        targets=["foo.dvc", "bar.dvc"],
        force=False,
        recursive=False,
        relink=True,
        with_deps=True,
    )


def test_log_summary(caplog):
    stats = {
        "added": ["file1", "file2", "file3"],
        "deleted": ["file4", "file5"],
        "modified": ["file6", "file7"],
    }

    def _assert_output(stats, expected_text):
        with caplog.at_level(logging.INFO, logger="dvc"):
            caplog.clear()
            log_summary(stats)
            assert expected_text in caplog.text

    _assert_output(stats, "3 added, 2 deleted and 2 modified")

    del stats["deleted"][1]
    _assert_output(stats, "3 added, 1 deleted and 2 modified")

    del stats["deleted"][0]
    _assert_output(stats, "3 added and 2 modified")

    del stats["modified"]
    _assert_output(stats, "3 added")

    _assert_output({}, "")


def test_log_changes(caplog):
    stats = {
        "added": ["file1", "dir1/"],
        "deleted": ["dir2/"],
        "modified": ["file2"],
    }

    from itertools import zip_longest

    def _assert_output(stats, expected_outs):
        with caplog.at_level(logging.INFO, logger="dvc"):
            caplog.clear()
            log_changes(stats)
            actual_output = caplog.text.splitlines()
            for out, line in zip_longest(expected_outs, actual_output):
                assert out in line

    _assert_output(stats, ["M\tfile2", "A\tfile1", "A\tdir1/", "D\tdir2/"])

    del stats["deleted"][0]
    _assert_output(stats, ["M\tfile2", "A\tfile1", "A\tdir1/"])

    del stats["modified"]
    _assert_output(stats, ["A\tfile1", "A\tdir1/"])
