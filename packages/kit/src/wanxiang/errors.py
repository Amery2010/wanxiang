class WXError(Exception):
    def __init__(self, code, message, *, details=None, node=None):
        super().__init__(message)
        self.code, self.message, self.details, self.node = code, message, details or {}, node
    def to_dict(self):
        return {"code": self.code, "message": self.message, "node": self.node, "details": self.details}

EXIT_CODES = {"ASSET_RETIRED": 2, "RECIPE_INVALID": 2, "INPUT_INVALID": 2, "PATH_UNSAFE": 2,
              "CAPABILITY_MISSING": 3, "BUDGET_EXCEEDED": 4, "GEOMETRY_INVALID": 5,
              "OUTPUT_MISMATCH": 6, "VALIDATION_FAILED": 6, "HOST_ASSET_MISSING": 7,
              "FORMAT_UNSUPPORTED": 3, "CANCELLED": 8, "REVIEW_INCOMPLETE": 8}
