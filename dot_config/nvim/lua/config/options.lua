vim.g.mapleader = " "

vim.opt.relativenumber = true
vim.opt.number         = true
vim.opt.tabstop        = 2
vim.opt.shiftwidth     = 2
vim.opt.expandtab      = true
vim.opt.smartindent    = true
vim.opt.wrap           = false
vim.opt.termguicolors  = true
vim.opt.signcolumn     = "yes"
vim.opt.updatetime     = 300
vim.opt.autoread       = true
vim.opt.clipboard      = "unnamedplus"
vim.opt.scrolloff      = 8
vim.opt.cursorline     = true

vim.opt.foldmethod     = "expr"
vim.opt.foldexpr = "v:lua.vim.treesitter.foldexpr()"
vim.opt.foldenable     = false
vim.opt.foldlevel      = 99
