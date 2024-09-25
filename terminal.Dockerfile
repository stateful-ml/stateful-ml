FROM docker:dind
COPY ./workspace /workspace
ENTRYPOINT ["sleep", "infinity"]
