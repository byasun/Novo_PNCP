import React from "react";

// Componente de barra de navegação principal.
// Props:
// - className: classes CSS adicionais
// - children: conteúdo da barra de navegação
// - ...props: demais props do elemento nav
const Navbar = ({ className = "", children, ...props }) => (
  <nav className={`nav ${className}`.trim()} {...props}>
    {children}
  </nav>
);

export default Navbar;
