FROM python:3.9.17-buster

# Arguments for Git configurations
ARG GITLAB_USER_NAME
ARG GITLAB_USER_EMAIL
ARG REMOTE_REPOSITORY
ARG PAGES_BRANCH=pages
ARG CI_COMMIT_BRANCH
ARG DOC_VERSION

# Set environment variable for the pages branch
ENV PAGES_BRANCH=$PAGES_BRANCH

# Set absolute path for WORKDIR
WORKDIR /home/wisenut/app
COPY ./ ./

RUN pip3 install --no-cache-dir -r ./docs/requirements.txt
RUN git config --global user.name "$GITLAB_USER_NAME" && \
    git config --global user.email "$GITLAB_USER_EMAIL" && \
    git remote set-url origin "$REMOTE_REPOSITORY" && \
    git fetch origin --depth=1
RUN git checkout -b "$CI_COMMIT_BRANCH" origin/"$CI_COMMIT_BRANCH"

# Set the docs directory as the working directory
WORKDIR /home/wisenut/app/docs

RUN git add . && \
    mike deploy --update-aliases "$DOC_VERSION" latest --branch "$PAGES_BRANCH" --deploy-prefix public && \
    mike set-default latest --branch "$PAGES_BRANCH" --deploy-prefix public

EXPOSE 8080

CMD ["sh", "-c", "mike serve --dev-addr 0.0.0.0:8080 --branch $PAGES_BRANCH"]