# [IMPORTANT] Dev instruction

## Step 1: Create another branch from this `dev` branch

- Make sure to checkout to `dev` and have the latest version of `dev`:

``` bash
git checkout dev
git pull origin dev
```

- Than create new branch with this naming convention: `[type]/[description]`

``` bash
# When creating a new feature
git checkout -b feat/gui

# When fixing a bug
git checkout -b fix/ui-bug

# When doing a chore (non development task)
git checkout -b chore/update-readme
```

## Step 2: Commit & Push

After finish your job, commiting the changes and push the branch to remote.

``` bash
git add .
git commit -m "fix: some existed bugs"
git push origin fix/ui-bugs
```

## Step 3: Create a Pull Request

After pushing your branch to remote, access GitHub Repo and create a Pull Request to `dev`. 

**PLEASE NOTICE!!! ONLY CREATE A PULL REQUEST TO `dev`, NOT `main`. PAY ATTENTION WHEN CREATING A PULL REQUEDST. THANK YOU!!!**

Always choose a reviewer for your pull request, it shouldn't be self-reviewed. Or at least notify other members via text message. You shouldn't merging to `dev` without any other member's reviews.