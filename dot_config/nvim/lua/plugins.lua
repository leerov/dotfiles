local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({

  {
    "sainnhe/gruvbox-material",
    lazy = false,
    priority = 1000,
    config = function()
      vim.cmd("colorscheme gruvbox-material")
    end,
  },

  {
    "josstei/whisk.nvim",
    event = "VeryLazy",
    opts = {
      cursor = {
        duration = 150,
        easing = "ease-out",
        enabled = true,
      },
      scroll = {
        duration = 200,
        easing = "ease-in-out",
        enabled = true,
      },
    },
  },

  {
    "nvim-tree/nvim-tree.lua",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      local function on_attach(bufnr)
        local api = require("nvim-tree.api")
        api.config.mappings.default_on_attach(bufnr)

        local function edit_and_close()
          local node = api.tree.get_node_under_cursor()
          if node and node.type == "file" then
            api.node.open.edit(node)
            api.tree.close()
          else
            api.node.open.edit(node)
          end
        end

        vim.keymap.set("n", "<CR>", edit_and_close, { buffer = bufnr, noremap = true, silent = true })
        vim.keymap.set("n", "o",    edit_and_close, { buffer = bufnr, noremap = true, silent = true })
        vim.keymap.set("n", "<2-LeftMouse>", edit_and_close, { buffer = bufnr, noremap = true, silent = true })
      end

      require("nvim-tree").setup({
        on_attach     = on_attach,
        view          = { width = 30, side = "left" },
        disable_netrw = true,
        hijack_netrw  = true,
      })
      vim.keymap.set("n", "<leader>e", "<cmd>NvimTreeToggle<CR>")
    end,
  },

  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("lualine").setup({
        options = {
          theme = "auto",
        },
      })
    end,
  },

  {
    "nvim-telescope/telescope.nvim",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      require("telescope").setup({
        defaults = {
          mappings = {
            i = { ["<Esc>"] = require("telescope.actions").close },
          },
        },
      })
      vim.keymap.set("n", "<leader>f",  "<cmd>Telescope current_buffer_fuzzy_find<CR>", { desc = "Search in file" })
      vim.keymap.set("n", "<leader>sf", "<cmd>Telescope live_grep<CR>",                { desc = "Search in project" })
      vim.keymap.set("n", "<C-p>",   "<cmd>Telescope find_files<CR>", { desc = "Find files" })
      vim.keymap.set("n", "<C-S-p>", "<cmd>Telescope commands<CR>",   { desc = "Command palette" })
    end,
  },

  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate",
    event = { "BufReadPost", "BufNewFile" },
    config = function()
      require("nvim-treesitter").setup({
        ensure_installed = { "lua", "python", "bash", "markdown" },
        highlight        = { enable = true },
        indent           = { enable = true },
      })
    end,
  },

  {
    "folke/trouble.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      require("trouble").setup()
    end,
  },

  {
    "lewis6991/gitsigns.nvim",
    config = function()
      require("gitsigns").setup({
        on_attach = function(bufnr)
          local gs = package.loaded.gitsigns
          local function bmap(mode, l, r, desc)
            vim.keymap.set(mode, l, r, { buffer = bufnr, desc = desc })
          end
          bmap("n", "]c", gs.next_hunk,        "Next hunk")
          bmap("n", "[c", gs.prev_hunk,        "Prev hunk")
          bmap("n", "<leader>gp", gs.preview_hunk, "Preview hunk")
          bmap("n", "<leader>gr", gs.reset_hunk,   "Reset hunk")
        end,
      })
    end,
  },

  {
    "folke/which-key.nvim",
    event  = "VeryLazy",
    config = function() require("which-key").setup() end,
  },


  {
    "hrsh7th/nvim-cmp",
    dependencies = {
      "hrsh7th/cmp-nvim-lsp",
      "hrsh7th/cmp-buffer",
      "hrsh7th/cmp-path",
      "L3MON4D3/LuaSnip",
      "saadparwaiz1/cmp_luasnip",
    },
    config = function()
      local cmp     = require("cmp")
      local luasnip = require("luasnip")
      cmp.setup({
        snippet = {
          expand = function(args) luasnip.lsp_expand(args.body) end,
        },
        mapping = cmp.mapping.preset.insert({
          ["<C-Space>"] = cmp.mapping.complete(),
          ["<CR>"]      = cmp.mapping.confirm({ select = true }),
          ["<Tab>"]     = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_next_item()
            elseif luasnip.expand_or_jumpable() then luasnip.expand_or_jump()
            else fallback() end
          end, { "i", "s" }),
          ["<S-Tab>"]   = cmp.mapping(function(fallback)
            if cmp.visible() then cmp.select_prev_item()
            elseif luasnip.jumpable(-1) then luasnip.jump(-1)
            else fallback() end
          end, { "i", "s" }),
        }),
        sources = cmp.config.sources({
          { name = "nvim_lsp" },
          { name = "luasnip" },
          { name = "buffer" },
          { name = "path" },
        }),
      })
    end,
  },

  {
    "neovim/nvim-lspconfig",
    dependencies = { "hrsh7th/cmp-nvim-lsp" },
    config = function()
      require("config.lsp")
    end,
  },

  {
    "windwp/nvim-autopairs",
    event = "InsertEnter",
    config = function()
      require("nvim-autopairs").setup()
    end,
  },

  {
  "ellisonleao/glow.nvim",
  dependencies = { "nvim-lua/plenary.nvim" },
  config = function()
    require("glow").setup({
      border = "rounded",
      style  = "dark",
    })
    vim.keymap.set("n", "<leader>m", "<cmd>Glow<CR>", { desc = "Markdown preview" })
  end,
 },
})
