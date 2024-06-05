import pytest

from magpie.core import BasicProtocol


@pytest.mark.parametrize(('diff', 'ref'), [
    ("""--- before.py
+++ after.py
@@ -1,4 +1,4 @@
-bacon
-eggs
-ham
+python
+eggy
+hamster
 guido""", """\033[1m--- before.py\033[0m
\033[1m+++ after.py\033[0m
\033[36m@@ -1,4 +1,4 @@\033[0m
\033[31m-bacon\033[0m
\033[31m-eggs\033[0m
\033[31m-ham\033[0m
\033[32m+python\033[0m
\033[32m+eggy\033[0m
\033[32m+hamster\033[0m
 guido"""),
    ("""*** before.py
--- after.py
***************
*** 1,4 ****
! bacon
! eggs
! ham
  guido
--- 1,4 ----
! python
! eggy
! hamster
  guido""", """\033[1m*** before.py\033[0m
\033[1m--- after.py\033[0m
\033[36m***************\033[0m
\033[36m*** 1,4 ****\033[0m
\033[33m! bacon\033[0m
\033[33m! eggs\033[0m
\033[33m! ham\033[0m
  guido
\033[36m--- 1,4 ----\033[0m
\033[33m! python\033[0m
\033[33m! eggy\033[0m
\033[33m! hamster\033[0m
  guido"""),
])
def test_color_diff(diff, ref):
    assert BasicProtocol.color_diff(diff) == ref
