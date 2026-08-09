local map = function(mode, lhs, rhs, opts)
  vim.keymap.set(mode, lhs, rhs, vim.tbl_extend("force", { noremap = true, silent = true }, opts or {}))
end

map("n", "<F12>", function()
  local cursor = vim.api.nvim_win_get_cursor(0)
  vim.cmd("%y+")
  vim.api.nvim_win_set_cursor(0, cursor)
  vim.notify("Скопировано в буфер обмена", vim.log.levels.INFO)
end, { desc = "Copy all lines to clipboard" })

map("n", "<leader>w", "<cmd>w<CR>", { desc = "Save" })
map("n", "<leader>q", "<cmd>q<CR>", { desc = "Quit" })
map("n", "<Esc>", "<cmd>nohlsearch<CR>")

map("n", "<leader>h", "<C-w>h", { desc = "Window left" })
map("n", "<leader>j", "<C-w>j", { desc = "Window down" })
map("n", "<leader>k", "<C-w>k", { desc = "Window up" })
map("n", "<leader>l", "<C-w>l", { desc = "Window right" })

map("n", "<leader>H", ":leftabove vsplit<CR>",  { desc = "Copy window left" })
map("n", "<leader>L", ":rightbelow vsplit<CR>", { desc = "Copy window right" })
map("n", "<leader>K", ":topleft split<CR>",     { desc = "Copy window up" })
map("n", "<leader>J", ":botright split<CR>",    { desc = "Copy window down" })

map("n", "<leader>[", "zM", { desc = "Fold all" })
map("n", "<leader>]", "zR", { desc = "Unfold all" })

map("n", "<leader>t", "<cmd>tabnew<CR>", { desc = "New tab" })
map("n", "<leader>1", "1gt", { desc = "Tab 1" })
map("n", "<leader>2", "2gt", { desc = "Tab 2" })
map("n", "<leader>3", "3gt", { desc = "Tab 3" })
map("n", "<leader>4", "4gt", { desc = "Tab 4" })
map("n", "<leader>5", "5gt", { desc = "Tab 5" })
map("n", "<leader>6", "6gt", { desc = "Tab 6" })
map("n", "<leader>7", "7gt", { desc = "Tab 7" })
map("n", "<leader>8", "8gt", { desc = "Tab 8" })
map("n", "<leader>9", "9gt", { desc = "Tab 9" })
map("n", "<leader>0", "10gt", { desc = "Tab 10" })

map("n", "<leader>sr", ":%s/", { desc = "Search and replace in file", silent = false })

map("n", "<leader><leader>", "<cmd>terminal<CR>", { desc = "Open terminal" })
map("v", "<Tab>", ">gv", { desc = "Indent right" })
map("v", "<S-Tab>", "<gv", { desc = "Indent left" })
