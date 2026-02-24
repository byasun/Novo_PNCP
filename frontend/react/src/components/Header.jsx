import React from "react";

// Componente de cabeçalho da aplicação.
// Props:
// - className: classes CSS adicionais
// - children: conteúdo do cabeçalho
// - ...props: demais props do elemento header
const Header = ({ className = "", children, ...props }) => (
  <header className={`app__header ${className}`.trim()} {...props}>
    {children}
  </header>
);

export default Header;
