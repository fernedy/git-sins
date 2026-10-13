# git-sins demo GIF — reproducible two ways:
#   local:   cd assets && vhs demo.tape            (needs python3 + git in PATH)
#   docker:  docker run --rm -v "<repo parent>:/work" -w /work/git-sins/assets vhs-ops:1 demo.tape
#            (image recipe: .vhs/Dockerfile in the brand-work workspace)
Output demo.gif
Set FontSize 18
Set Width 1000
Set Height 640
Set Theme "Dracula"
Set TypingSpeed 20ms

Type "bash ./setup-demo.sh" Enter
Sleep 3s
Type "cd /tmp/demo && git log --oneline" Enter
Sleep 3s
Type "python3 ../git_sins.py /tmp/demo" Enter
Sleep 6s
