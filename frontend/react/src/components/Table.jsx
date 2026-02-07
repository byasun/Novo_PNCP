import React from "react";

const Table = ({ className = "", children, ...props }) => (
  <div className={`table ${className}`.trim()} {...props}>
    {children}
  </div>
);

const TableHead = ({ className = "", children, ...props }) => (
  <div className={`table__head ${className}`.trim()} {...props}>
    {children}
  </div>
);

const TableRow = ({ className = "", children, ...props }) => (
  <div className={`table__row ${className}`.trim()} {...props}>
    {children}
  </div>
);

export { Table, TableHead, TableRow };
