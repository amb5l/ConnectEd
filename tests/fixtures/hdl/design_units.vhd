library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity entity1 is
  generic (
    GENERIC1 : integer := 8;
    GENERIC2 : natural := 16
  );
  port (
    port1 : in    std_logic;
    port2 : out   std_logic;
    port3 : inout std_logic_vector(GENERIC1-1 downto 0)
  );
end entity entity1;

architecture architecture1 of entity1 is

  component component1 is
    generic (
      GENERIC1 : integer := 8;
      GENERIC2 : natural := 16
    );
    port (
      port1 : in    std_logic;
      port2 : out   std_logic;
      port3 : inout std_logic_vector(GENERIC1-1 downto 0)
    );
  end component component1;

begin
end architecture architecture1;

package package1 is

  component component2 is
    generic (
      GENERIC1 : integer := 8;
      GENERIC2 : natural := 16
    );
    port (
      port1 : in    std_logic;
      port2 : out   std_logic;
      port3 : inout std_logic_vector(GENERIC1-1 downto 0)
    );
  end component component2;

end package package1;
