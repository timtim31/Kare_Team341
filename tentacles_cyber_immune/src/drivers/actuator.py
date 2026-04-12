from idl.movement import MovementRequest

class ManipulatorDrivers:
    def execute(self, request: MovementRequest):
        """
        Физическое выполнение команды. 
        В реальности здесь был бы код управления моторами через GPIO или USB.
        """
        print(f"[HARDWARE] Выполнение: Щупальце №{request.arm_id} "
              f"движение в ({request.vector_x}, {request.vector_y}) "
              f"с мощностью {request.power}%")
        return True