import React from "react";

// Componente de tabela customizada.
// Props comuns:
// - className: classes CSS adicionais
// - children: conteúdo do componente
// - ...props: demais props do elemento div
const Table = ({ className = "", children, ...props }) => (
  <div className={`table ${className}`.trim()} {...props}>
    {children}
  </div>
);

// Cabeçalho da tabela
const TableHead = ({ className = "", children, ...props }) => (
  <div className={`table__head ${className}`.trim()} {...props}>
    {children}
  </div>
);

// Linha da tabela
const TableRow = ({ className = "", children, ...props }) => (
  <div className={`table__row ${className}`.trim()} {...props}>
    {children}
  </div>
);

export { Table, TableHead, TableRow };
