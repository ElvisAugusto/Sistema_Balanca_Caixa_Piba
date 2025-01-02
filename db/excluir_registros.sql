PRAGMA foreign_keys = 0;  -- Desativa a verificação de chaves estrangeiras

DELETE FROM bebida;  -- Exclui todos os registros da tabela bebida
DELETE FROM balanca;  -- Exclui todos os registros da tabela balanca

PRAGMA foreign_keys = 1;  -- Reativa a verificação de chaves estrangeiras
