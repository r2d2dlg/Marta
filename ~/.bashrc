# Unset NPM_CONFIG_PREFIX to avoid conflicts with NVM
unset NPM_CONFIG_PREFIX

# NVM Initialization
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Set default Node version to LTS
nvm alias default lts/*
nvm use default